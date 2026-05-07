import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from models.pump_system import ControlledPump
from models.tank_system import ControlledTank
from models.turbine_system import ControlledTurbine
from cloud.bigquery_uploader import BigQueryUploader
from core.core_logger import DataLogger

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
                    dcc.Graph(id='historical-graph'),
                    dbc.Button("Refresh History", id="btn-refresh-hist", color="info", className="mt-2")
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

if __name__ == '__main__':
    app.run(debug=True)