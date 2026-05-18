import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from google.cloud import bigquery

# Importamos tus modelos 
from models.pump_system import ControlledPump 
from models.tank_system import ControlledTank 
from models.turbine_system import ControlledTurbine 

app = FastAPI(title="Digital Twin API", version="2.0.0")

# --- CONFIGURACIÓN DE GOOGLE CLOUD ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"
bq_client = bigquery.Client()
# ACA VA EL NOMBRE DE TU TABLA:
TABLA_BIGQUERY = "digital_twin_data.telemetry"

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

sim_context = {
    "model": None,
    "name": "",
    "target": 0.0
}

class ControlConfig(BaseModel):
    target: float

# --- FUNCIÓN QUE CORRE EN SEGUNDO PLANO ---
def upload_to_bigquery(equipo: str, valor: float, target: float, valvula: float):
    """Sube una fila de telemetría a BQ silenciosamente"""
    try:
        fila = [{
            "timestamp": datetime.utcnow().isoformat(),
            "equipment": equipo,
            "target": target,
            "current_value": valor,
            "valve_pos": valvula
        }]
        errores = bq_client.insert_rows_json(TABLA_BIGQUERY, fila)
        if errores:
            print(f"❌ Error subiendo a BigQuery: {errores}")
    except Exception as e:
        print(f"⚠️ Falla de conexión a la nube: {e}")


@app.get("/")
async def root():
    return {
        "status": "online", 
        "message": "API RUN OK."
    }

@app.post("/sim/start/{equip_id}")
async def start_simulation(equip_id: str, config: ControlConfig):
    if equip_id == "1":
        sim_context["model"] = ControlledPump(MaxRPM=4000, kP=10.0, kI=0.0001, kD=0.01)
        sim_context["name"] = "Pump (RPM)"
    elif equip_id == "2":
        sim_context["model"] = ControlledTank(diameter=2.0, height=10.0, kP=12.0, kI=0.05, kD=0.1)
        sim_context["name"] = "Water Tank (Level %)"
    elif equip_id == "3":
        sim_context["model"] = ControlledTurbine(kP=0.8, kI=0.05, kD=0.1)
        sim_context["name"] = "Gas Turbine (RPM)"
    else:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    sim_context["target"] = config.target
    return {"message": f"Simulación de {sim_context['name']} iniciada", "target": config.target}

# BACKGROUND TASKS
@app.get("/sim/telemetry")
async def get_telemetry(background_tasks: BackgroundTasks):
    model = sim_context["model"]
    if not model:
        return {"status": "offline"}

    # Ejecución ciclo de control y física
    model.PID(
        input_val=model.sensor_value, 
        SetpointAuto=sim_context["target"], 
        automatic_mode=True, 
        SetpointMan=0.0
    )
    model.update(1)

    equipo = sim_context["name"]
    valor = round(model.sensor_value, 2)
    target = sim_context["target"]
    valvula = round(model.valve, 2)

    background_tasks.add_task(upload_to_bigquery, equipo, valor, target, valvula)

    return {
        "equipment": equipo,
        "value": valor,
        "target": target,
        "valve": valvula,
        "status": {
            "aux_motor": getattr(model, "aux_motor", False),
            "igniters": getattr(model, "igniters", False),
            "burners": getattr(model, "burners_on", False)
        }
    }

@app.get("/sim/analytics/{query_id}")
async def get_analytics(query_id: str, equip_name: str):
    # 1. Diccionario de consultas SQL predefinidas
    queries = {
        "recent": f"""
            SELECT timestamp, equipment, target, current_value, valve_pos 
            FROM `{TABLA_BIGQUERY}` 
            WHERE equipment = @equip_name 
            ORDER BY timestamp DESC 
            LIMIT 50
        """,
        "stats": f"""
            SELECT 
                equipment, 
                ROUND(AVG(current_value), 2) as avg_value, 
                ROUND(MAX(valve_pos), 2) as max_valve_aperture,
                COUNT(*) as total_records
            FROM `{TABLA_BIGQUERY}` 
            WHERE equipment = @equip_name 
            GROUP BY equipment
        """,
        "overspeed": f"""
            SELECT timestamp, current_value, target, (current_value - target) as deviation
            FROM `{TABLA_BIGQUERY}` 
            WHERE equipment = @equip_name AND current_value > (target + 50)
            ORDER BY timestamp DESC
            LIMIT 10
        """
    }

    # 2. Validación de seguridad
    if query_id not in queries:
        raise HTTPException(status_code=400, detail="Consulta no autorizada")

    # 3. Configuración de parámetros seguros
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("equip_name", "STRING", equip_name)
        ]
    )
    # 4. Ejecución
    try:
        query_job = bq_client.query(queries[query_id], job_config=job_config)
        resultados = [dict(row) for row in query_job]
        return {"data": resultados}
    except Exception as e:
        print(f"Error en BigQuery: {e}")
        raise HTTPException(status_code=500, detail="Error interno consultando la base de datos")



@app.get("/sim/history")
async def get_history(days: int = 7):
    return {"data": "Historial de BigQuery aquí"}