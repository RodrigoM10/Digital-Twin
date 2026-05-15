# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import dash
# from dash import dcc, html, Input, Output, State, ctx
# import dash_bootstrap_components as dbc
# import plotly.graph_objects as go
# import pandas_gbq
# import pandas as pd
# from datetime import datetime
# from plotly.subplots import make_subplots

# from models.pump_system import ControlledPump
# from models.tank_system import ControlledTank
# from models.turbine_system import ControlledTurbine
# from services.bigquery_uploader import BigQueryUploader
# from services.core_logger import DataLogger
# from google.oauth2 import service_account


# # ─────────────────────────────────────────────
# # CONFIGURACIÓN Y CREDENCIALES
# # ─────────────────────────────────────────────
# CREDENTIALS_PATH = "gcp_credentials.json"
# credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
# PROJECT_ID = credentials.project_id

# MAX_RPM_DISPLAY = 12000  # Constante para la barra de progreso

# # ─────────────────────────────────────────────
# # ESTADO GLOBAL DE LA SIMULACIÓN
# # ─────────────────────────────────────────────
# sim_state = {
#     "active": False,
#     "model": None,
#     "data": [],
#     "equipment_name": "",
#     "logger": None
# }

# # ─────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────
# LED_BASE_STYLE = {"display": "inline-block", "width": "12px", "height": "12px", "borderRadius": "50%"}

# def get_led_style(state: bool) -> dict:
#     """Devuelve el estilo CSS de un indicador LED según su estado."""
#     return {**LED_BASE_STYLE, "backgroundColor": "#28a745" if state else "gray"}

# OFFLINE_LED = {**LED_BASE_STYLE, "backgroundColor": "gray"}

# EQUIP_NAMES = {
#     "1": "Pump (RPM)",
#     "2": "Water Tank (Level %)",
#     "3": "Gas Turbine (RPM)"
# }

# # ─────────────────────────────────────────────
# # APP
# # ─────────────────────────────────────────────
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# app.layout = dbc.Container([
#     dbc.Row([
#         dbc.Col(html.H1("Digital Twin Integrated Control", className="text-center mt-4"), width=12)
#     ]),
#     dbc.Row([
#         dbc.Col([
#             dbc.Card([
#                 dbc.CardBody([
#                     html.H5("Simulation Setup"),
#                     dcc.Dropdown(
#                         id='equip-selector',
#                         options=[
#                             {'label': 'Pump (RPM)', 'value': '1'},
#                             {'label': 'Water Tank (Level %)', 'value': '2'},
#                             {'label': 'Gas Turbine (RPM)', 'value': '3'}
#                         ],
#                         value='1'
#                     ),
#                     html.Label("Target Value:", className="mt-3"),
#                     dcc.Input(id='target-val', type='number', value=1000, className="form-control"),

#                     dbc.Button("START SIMULATION", id="btn-start", color="success", className="w-100 mt-4"),
#                     dbc.Button("STOP & UPLOAD TO CLOUD", id="btn-stop", color="danger", className="w-100 mt-2", disabled=True),

#                     html.Div(id="sim-status", className="mt-3 text-center fw-bold")
#                 ])
#             ]),
#             dbc.Card([
#                 dbc.CardHeader(html.H5("Unit Status Monitor", className="mb-0")),
#                 dbc.CardBody([
#                     html.Div([
#                         html.Span("MODE: "),
#                         dbc.Badge("------", id="status-mode", color="secondary", className="ms-2"),
#                     ], className="mb-3 text-center"),

#                     html.Div([
#                         html.Small("DIGITAL INDICATORS", className="text-muted d-block mb-2 text-center"),
#                         dbc.Row([
#                             dbc.Col([
#                                 html.Div([
#                                     html.Span(id="led-aux", className="rounded-circle me-2",
#                                               style={**LED_BASE_STYLE, "backgroundColor": "gray"}),
#                                     html.Small("Aux Motor")
#                                 ]),
#                                 html.Div([
#                                     html.Span(id="led-joint", className="rounded-circle me-2",
#                                               style={**LED_BASE_STYLE, "backgroundColor": "gray"}),
#                                     html.Small("Pneum. Joint")
#                                 ]),
#                             ], width=6),
#                             dbc.Col([
#                                 html.Div([
#                                     html.Span(id="led-igniters", className="rounded-circle me-2",
#                                               style={**LED_BASE_STYLE, "backgroundColor": "gray"}),
#                                     html.Small("Igniters")
#                                 ]),
#                                 html.Div([
#                                     html.Span(id="led-burners", className="rounded-circle me-2",
#                                               style={**LED_BASE_STYLE, "backgroundColor": "gray"}),
#                                     html.Small("Burners")
#                                 ]),
#                             ], width=6),
#                         ]),
#                     ], className="mb-4"),

#                     html.Div([
#                         html.Small("SPEED UTILIZATION", className="text-muted"),
#                         dbc.Progress(id="status-bar", value=0, striped=True, animated=True, className="mt-1", style={"height": "20px"}),
#                     ], className="mb-3"),

#                     html.Div(id="status-alert", className="p-2 text-center small fw-bold",
#                              style={"border": "1px solid #ddd", "borderRadius": "5px"})
#                 ])
#             ], className="mt-4")
#         ], width=3),

#         dbc.Col([
#             dbc.Tabs([
#                 dbc.Tab(
#                     children=[
#                         dcc.Graph(id='realtime-graph'),
#                         dcc.Interval(id='sim-interval', interval=1000, disabled=True)
#                     ],
#                     label="Real-Time Monitor"
#                 ),
#                 dbc.Tab(
#                     children=[
#                         dbc.Row([
#                             dbc.Col([
#                                 html.Label("Date Range:", className="mt-2"),
#                                 dcc.DatePickerRange(
#                                     id='history-date-range',
#                                     start_date=pd.Timestamp.now().date() - pd.Timedelta(days=7),
#                                     end_date=pd.Timestamp.now().date(),
#                                     display_format='YYYY-MM-DD',
#                                     className="mb-3"
#                                 ),
#                             ], width=6),
#                             dbc.Col([
#                                 dbc.Button("FETCH DATA FROM CLOUD", id="btn-fetch-history",
#                                            color="primary", className="mt-4 w-100")
#                             ], width=4)
#                         ]),
#                         dcc.Loading(
#                             id="loading-history",
#                             type="default",
#                             children=dcc.Graph(id='historical-graph')
#                         )
#                     ],
#                     label="Historical Data (Cloud)"
#                 ),
                
#             ])
#         ], width=9)
#     ])
# ], fluid=True)


# # ─────────────────────────────────────────────
# # CALLBACK: CONTROL DE SIMULACIÓN
# # ─────────────────────────────────────────────
# @app.callback(
#     [Output("sim-interval", "disabled"),
#      Output("btn-start", "disabled"),
#      Output("btn-stop", "disabled"),
#      Output("sim-status", "children")],
#     [Input("btn-start", "n_clicks"),
#      Input("btn-stop", "n_clicks")],
#     [State("equip-selector", "value"),
#      State("target-val", "value")],
#     prevent_initial_call=True  # CORRECCIÓN: evita disparo al cargar la página
# )
# def manage_simulation(n_start, n_stop, equip_id, target):
#     trigger = ctx.triggered_id

#     if trigger == "btn-start":
#         # CORRECCIÓN: bloque completo dentro del if, indentación corregida
#         if equip_id == "1":
#             sim_state["model"] = ControlledPump(MaxRPM=4000, kP=10.0, kI=0.0001, kD=0.01)
#             sim_state["equipment_name"] = "Pump (RPM)"
#         elif equip_id == "2":
#             sim_state["model"] = ControlledTank(diameter=2.0, height=10.0, kP=12.0, kI=0.05, kD=0.1)
#             sim_state["equipment_name"] = "Water Tank (Level %)"
#         elif equip_id == "3":
#             sim_state["model"] = ControlledTurbine(kP=0.8, kI=0.05, kD=0.1)
#             sim_state["equipment_name"] = "Gas Turbine (RPM)"

#         sim_state["active"] = True
#         sim_state["data"] = []

#         sim_state["logger"] = DataLogger(filename=f"dash_log_{equip_id}.csv")

#         return False, True, False, "🔴 SIMULATING..."

#     if trigger == "btn-stop":
#         sim_state["active"] = False
#         # CORRECCIÓN: manejo de errores en la subida a la nube
#         try:
#             uploader = BigQueryUploader()
#             uploader.upload_log_to_bq(sim_state["logger"].filepath)
#             return True, False, True, "✅ Uploaded to Cloud"
#         except Exception as e:
#             return True, False, True, f"⚠️ Upload failed: {e}"

#     return True, False, True, "Ready"


# # ─────────────────────────────────────────────
# # CALLBACK: ACTUALIZACIÓN EN TIEMPO REAL
# # ─────────────────────────────────────────────
# @app.callback(
#     [Output("realtime-graph", "figure"),
#      Output("status-mode", "children"),
#      Output("status-mode", "color"),
#      Output("status-bar", "value"),
#      Output("status-bar", "label"),
#      Output("status-alert", "children"),
#      Output("status-alert", "style"),
#      Output("led-aux", "style"),
#      Output("led-joint", "style"),
#      Output("led-igniters", "style"),
#      Output("led-burners", "style")],
#     Input("sim-interval", "n_intervals"),
#     State("target-val", "value")
# )
# def update_physics_and_ui(n, target):
#     # CORRECCIÓN: retorno offline con estilos LED completos (antes eran dicts vacíos {})
#     if not sim_state["active"] or sim_state["model"] is None:
#         return (
#             go.Figure(),
#             "OFFLINE", "secondary",
#             0, "",
#             "WAITING", {"border": "1px solid #ddd", "borderRadius": "5px"},
#             OFFLINE_LED, OFFLINE_LED, OFFLINE_LED, OFFLINE_LED
#         )

#     model = sim_state["model"]

#     model.PID(input_val=model.sensor_value, automatic_mode=model.auto_mode,
#               SetpointAuto=target, SetpointMan=model.valve)
#     model.update(1)

#     # --- Modo de operación ---
#     mode_text = "READY"
#     mode_color = "info"
#     if model.sensor_value == 0:
#         mode_text, mode_color = "STOP", "dark"
#     elif getattr(model, 'emergency_stop', False):
#         mode_text, mode_color = "EMERGENCY", "danger"
#     elif model.auto_mode:
#         mode_text, mode_color = "AUTO-CONTROL", "success"

#     # --- Alerta de estado ---
#     alert_text = "SYSTEM NORMAL"
#     alert_style = {"backgroundColor": "#d4edda", "color": "#155724", "border": "1px solid #ddd", "borderRadius": "5px"}
#     if model.sensor_value > target + 100:
#         alert_text = "OVER-SPEED WARNING"
#         alert_style = {"backgroundColor": "#f8d7da", "color": "#721c24", "border": "1px solid #ddd", "borderRadius": "5px"}

#     # --- LEDs ---
#     led_aux   = get_led_style(getattr(model, 'aux_motor', False))
#     led_joint = get_led_style(getattr(model, 'pneumatic_joint', False))
#     led_ign   = get_led_style(getattr(model, 'igniters', False))
#     led_burn  = get_led_style(getattr(model, 'burners_on', False))

#     # --- Barra de progreso ---
#     progress_val = min(int((model.sensor_value / MAX_RPM_DISPLAY) * 100), 100)
#     progress_label = f"{progress_val}%"

#     # --- Log ---
#     sim_state["logger"].log_data(
#         equipment_name=sim_state["equipment_name"],
#         target=target,
#         current_value=model.sensor_value,
#         valve_pos=model.valve
#     )

#     # --- Gráfico ---
#     sim_state["data"].append({
#         "time": datetime.now(),
#         "val": model.sensor_value,
#         "target": target
#     })

#     df = pd.DataFrame(sim_state["data"])
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df["time"], y=df["val"], name="Real Value"))
#     fig.add_trace(go.Scatter(x=df["time"], y=df["target"], name="Target", line=dict(dash='dash')))
#     fig.update_layout(title="Real-Time Digital Twin Performance", margin=dict(t=30, b=10))

#     return fig, mode_text, mode_color, progress_val, progress_label, alert_text, alert_style, led_aux, led_joint, led_ign, led_burn


# # ─────────────────────────────────────────────
# # CALLBACK: DATOS HISTÓRICOS
# # ─────────────────────────────────────────────
# @app.callback(
#     Output('historical-graph', 'figure'),
#     Input('btn-fetch-history', 'n_clicks'),
#     [State('equip-selector', 'value'),
#      State('history-date-range', 'start_date'),
#      State('history-date-range', 'end_date')],
#     prevent_initial_call=True  # CORRECCIÓN: evita query vacía al cargar
# )
# def update_historical_graph(n_clicks, equip_id, start_date, end_date):
#     selected_name = EQUIP_NAMES.get(equip_id, "Pump (RPM)")

#     # CORRECCIÓN: parámetros separados para evitar SQL injection
#     query = f"""
#         SELECT timestamp, target, current_value, valve_pos 
#         FROM `{PROJECT_ID}.digital_twin_data.telemetry` 
#         WHERE equipment = @equipment_name
#         AND timestamp >= @start_ts
#         AND timestamp <= @end_ts
#         ORDER BY timestamp ASC
#     """

#     query_config = {
#         "query": {
#             "parameterMode": "NAMED",
#             "queryParameters": [
#                 {"name": "equipment_name", "parameterType": {"type": "STRING"}, "parameterValue": {"value": selected_name}},
#                 {"name": "start_ts",       "parameterType": {"type": "STRING"}, "parameterValue": {"value": f"{start_date} 00:00:00"}},
#                 {"name": "end_ts",         "parameterType": {"type": "STRING"}, "parameterValue": {"value": f"{end_date} 23:59:59"}},
#             ]
#         }
#     }

#     print(f"DEBUG: Running Query for '{selected_name}' from {start_date} to {end_date}...")

#     try:
#         df_hist = pandas_gbq.read_gbq(
#             query,
#             project_id=PROJECT_ID,
#             credentials=credentials,
#             configuration=query_config
#         )

#         if df_hist.empty:
#             check_query = f"SELECT COUNT(*) as total FROM `{PROJECT_ID}.digital_twin_data.telemetry` WHERE equipment = @equipment_name"
#             count_res = pandas_gbq.read_gbq(
#                 check_query,
#                 project_id=PROJECT_ID,
#                 credentials=credentials,
#                 configuration={
#                     "query": {
#                         "parameterMode": "NAMED",
#                         "queryParameters": [
#                             {"name": "equipment_name", "parameterType": {"type": "STRING"}, "parameterValue": {"value": selected_name}},
#                         ]
#                     }
#                 }
#             )
#             total = count_res['total'][0]
#             return go.Figure().update_layout(title=f"No data found for this range. (Total Historical Data: {total})")

#         fig = make_subplots(specs=[[{"secondary_y": True}]])

#         fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['current_value'],
#                                  name='Value', line=dict(color='#007bff')), secondary_y=False)
#         fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['target'],
#                                  name='Target', line=dict(color='#dc3545', dash='dot')), secondary_y=False)
#         fig.add_trace(go.Bar(x=df_hist['timestamp'], y=df_hist['valve_pos'],
#                              name='Valve %', opacity=0.3, marker_color='gray'), secondary_y=True)

#         fig.update_layout(
#             title=f"Historical Analysis: {selected_name}",
#             xaxis_title="Time",
#             template="plotly_white",
#             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
#         )
#         fig.update_yaxes(title_text="<b>Process</b> Value", secondary_y=False)
#         fig.update_yaxes(title_text="<b>Valve</b> Position %", secondary_y=True, range=[0, 100])

#         return fig

#     except Exception as e:
#         return go.Figure().update_layout(title=f"Error: {e}")


# if __name__ == '__main__':
#     app.run(debug=True)