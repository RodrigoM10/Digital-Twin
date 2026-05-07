import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas_gbq
import pandas as pd
from datetime import datetime

from models.pump_system import ControlledPump
from models.tank_system import ControlledTank
from models.turbine_system import ControlledTurbine
from cloud.bigquery_uploader import BigQueryUploader
from core.core_logger import DataLogger
from google.oauth2 import service_account


CREDENTIALS_PATH = "gcp_credentials.json"
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
PROJECT_ID = credentials.project_id

sim_state = {
    "active": False,
    "model": None,
    "data": [], 
    "equipment_name": "",
    "logger": None
}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Digital Twin Integrated Control", className="text-center mt-4"), width=12)
    ]),

    dbc.Row([
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Simulation Setup"),
                    dcc.Dropdown(
                        id='equip-selector',
                        options=[
                            {'label': 'Pump (RPM)', 'value': '1'},
                            {'label': 'Water Tank (Level %)', 'value': '2'},
                            {'label': 'Gas Turbine (RPM)', 'value': '3'}
                        ],
                        value='1'
                    ),
                    html.Label("Target Value:", className="mt-3"),
                    dcc.Input(id='target-val', type='number', value=1000, className="form-control"),
                    
                    dbc.Button("START SIMULATION", id="btn-start", color="success", className="w-100 mt-4"),
                    dbc.Button("STOP & UPLOAD TO CLOUD", id="btn-stop", color="danger", className="w-100 mt-2", disabled=True),
                    
                    html.Div(id="sim-status", className="mt-3 text-center fw-bold")
                ])
            ])
        ], width=3),

        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Real-Time Monitor", children=[
                    dcc.Graph(id='realtime-graph'),
                    dcc.Interval(id='sim-interval', interval=1000, disabled=True) 
                ]),
                dbc.Tab(label="Historical Data (Cloud)", children=[
                    dbc.Row([
                        dbc.Col([
                            html.Label("Date Range:", className="mt-2"),
                            dcc.DatePickerRange(
                                id='history-date-range',
                                start_date=pd.Timestamp.now().date() - pd.Timedelta(days=7),
                                end_date=pd.Timestamp.now().date(),
                                display_format='YYYY-MM-DD',
                                className="mb-3"
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Button("FETCH DATA FROM CLOUD", id="btn-fetch-history", 
                                    color="primary", className="mt-4 w-100")
                        ], width=4)
                    ]),
                    dcc.Loading( # Esto muestra un spinner mientras BigQuery responde
                        id="loading-history",
                        type="default",
                        children=dcc.Graph(id='historical-graph')
                    )
                ]),
            ])
        ], width=9)
    ])
], fluid=True)

@app.callback(
    [Output("sim-interval", "disabled"),
     Output("btn-start", "disabled"),
     Output("btn-stop", "disabled"),
     Output("sim-status", "children")],
    [Input("btn-start", "n_clicks"),
     Input("btn-stop", "n_clicks")],
    [State("equip-selector", "value"),
     State("target-val", "value")]
)
def manage_simulation(n_start, n_stop, equip_id, target):
    trigger = ctx.triggered_id
    
    if trigger == "btn-start":
        if equip_id == "1":
            sim_state["model"] = ControlledPump(MaxRPM=4000, kP=10.0, kI=0.0001, kD=0.01)
            sim_state["equipment_name"] = "Pump (RPM)"
        if equip_id == "2":
            sim_state["model"] = ControlledTank(diameter=2.0, height=10.0, kP=12.0, kI=0.05, kD=0.1)
            sim_state["equipment_name"] = "Water Tank (Level %)"
        if equip_id == "3":
            sim_state["model"] = ControlledTurbine(kP=0.8, kI=0.05, kD=0.1)
            sim_state["equipment_name"] = "Gas Turbine (RPM)"
    

        sim_state["active"] = True
        sim_state["data"] = [] 
        sim_state["logger"] = DataLogger(filname=f"dash_log_{equip_id}.csv")
        
        return False, True, False, "🔴 SIMULATING..."

    if trigger == "btn-stop":
        sim_state["active"] = False
        # Al detener, disparamos la subida
        uploader = BigQueryUploader()
        uploader.upload_log_to_bq(sim_state["logger"].filepath)
        
        return True, False, True, "✅ Uploaded to Cloud"

    return True, False, True, "Ready"

@app.callback(
    Output("realtime-graph", "figure"),
    Input("sim-interval", "n_intervals"),
    State("target-val", "value")
)
def update_physics_and_ui(n, target):
    if not sim_state["active"] or sim_state["model"] is None:
        return go.Figure()

    model = sim_state["model"]
    model.PID(input_val=model.sensor_value, automatic_mode=model.auto_mode, 
              SetpointAuto=target, SetpointMan=model.valve)
    model.update(1) 

    sim_state["logger"].log_data(
        equipment_name=sim_state["equipment_name"],
        target=target,
        current_value=model.sensor_value,
        valve_pos=model.valve
    )

    new_point = {
        "time": datetime.now(),
        "val": model.sensor_value,
        "target": target
    }
    sim_state["data"].append(new_point)
    
    df = pd.DataFrame(sim_state["data"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["val"], name="Real Value"))
    fig.add_trace(go.Scatter(x=df["time"], y=df["target"], name="Target", line=dict(dash='dash')))
    fig.update_layout(title="Real-Time Digital Twin Performance", margin=dict(t=30, b=10))
    
    return fig

@app.callback(
    Output('historical-graph', 'figure'),
    Input('btn-fetch-history', 'n_clicks'),
    State('equip-selector', 'value'),
    State('history-date-range', 'start_date'),
    State('history-date-range', 'end_date')
)
def update_historical_graph(n_clicks, equip_id, start_date, end_date):
    if n_clicks is None:
        return go.Figure().update_layout(title="Click to load historical data")

    # Mapeo de ID a Nombre real para la query
    equip_names = {"1": "Pump (RPM)", "2": "Water Tank (Level %)", "3": "Gas Turbine (RPM)"}
    selected_name = equip_names.get(equip_id, "Pump (RPM)")

    query = f"""
        SELECT timestamp, target, current_value, valve_pos 
        FROM `{PROJECT_ID}.digital_twin_data.telemetry` 
        WHERE equipment = '{selected_name}' 
        AND timestamp BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY timestamp ASC
    """
    
    try:
        df_hist = pandas_gbq.read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
        
        if df_hist.empty:
            return go.Figure().update_layout(title="No data found for this range")

        # Crear gráfico avanzado con doble eje Y
        from plotly.subplots import make_subplots
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Eje Y Primario (Variables de Proceso)
        fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['current_value'], 
                                 name='Value', line=dict(color='#007bff')), secondary_y=False)
        fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['target'], 
                                 name='Target', line=dict(color='#dc3545', dash='dot')), secondary_y=False)

        # Eje Y Secundario (Válvula %)
        fig.add_trace(go.Bar(x=df_hist['timestamp'], y=df_hist['valve_pos'], 
                             name='Valve %', opacity=0.3, marker_color='gray'), secondary_y=True)

        fig.update_layout(
            title=f"Historical Analysis: {selected_name}",
            xaxis_title="Time",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_yaxes(title_text="<b>Process</b> Value", secondary_y=False)
        fig.update_yaxes(title_text="<b>Valve</b> Position %", secondary_y=True, range=[0, 100])

        return fig

    except Exception as e:
        return go.Figure().update_layout(title=f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True)