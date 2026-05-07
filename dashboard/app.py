import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas_gbq
from google.oauth2 import service_account

CREDENTIALS_PATH = "gcp_credentials.json"
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
PROJECT_ID = credentials.project_id


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Digital Twin Control Center", className="text-center mt-4 mb-4"), width=12)
    ]),
    
    dbc.Row([
        # Columna de controles
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Configuration"),
                    html.Label("Selected Equipment:"),
                    dcc.Dropdown(
                        id='equip-selector',
                        options=[
                            {'label': 'Pump (RPM)', 'value': 'Pump (RPM)'},
                            {'label': 'Gas Turbine (RPM)', 'value': 'Gas Turbine (RPM)'},
                            {'label': 'Water Tank (Level %)', 'value': 'Water Tank (Level %)'}
                        ],
                        value='Pump (RPM)',
                        clearable=False
                    ),
                    html.Hr(),
                    html.P("State: Connected with BigQuery ✅", className="text-success")
                ])
            ], className="mb-4")
        ], width=3),

        # Columna de Visualización
        dbc.Col([
            # Fila de KPIs
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Current Value"),
                        html.H3(id="kpi-current", className="text-primary")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Target"),
                        html.H3(id="kpi-target", className="text-danger")
                    ])
                ]), width=4),
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Valve Position"),
                        html.H3(id="kpi-valve", className="text-success")
                    ])
                ]), width=4),
            ], className="mb-4"),

            # Gráfico principal
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='live-graph')
                ])
            ])
        ], width=9)
    ]),

    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
], fluid=True)

@app.callback(
    [Output('live-graph', 'figure'),
     Output('kpi-current', 'children'),
     Output('kpi-target', 'children'),
     Output('kpi-valve', 'children')],
    [Input('equip-selector', 'value'),
     Input('interval-component', 'n_intervals')]
)

def update_dashboard(selected_equip, n):
    query = f"SELECT * FROM `{PROJECT_ID}.digital_twin_data.telemetry` WHERE equipment = '{selected_equip}' ORDER BY timestamp DESC LIMIT 50"
    df = pandas_gbq.read_gbq(query, project_id=PROJECT_ID, credentials=credentials)

    if df.empty:
        return go.Figure(), "--", "--", "--"

    latest = df.iloc[0]
    
    df_plot = df.sort_values('timestamp')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['timestamp'], y=df_plot['current_value'], name='Actual', line=dict(color='#007bff')))
    fig.add_trace(go.Scatter(x=df_plot['timestamp'], y=df_plot['target'], name='Target', line=dict(color='#dc3545', dash='dash')))
    
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=400, template="plotly_white")

    return fig, f"{latest['current_value']:.1f}", f"{latest['target']:.1f}", f"{latest['valve_pos']:.1f}%"

if __name__ == '__main__':
    app.run(debug=True)