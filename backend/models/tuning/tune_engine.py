"""
================================================================================
 TUNE ENGINE  ·  Orquestador de sintonización analítica por respuesta al escalón
================================================================================

Punto de entrada del toolkit de sintonización. Ensambla, mediante inyección de
dependencias, las piezas desacopladas del paquete ``tuning``:

    plants/        -> física de la planta            (PumpPlant)
    simulation/    -> motor de experimentos          (Open/Closed loop)
    identification/-> ajuste del modelo del proceso  (FOPDT, método de Smith)
    tuning_rules/  -> reglas de ganancias            (Ziegler-Nichols, Cohen-Coon)
    controllers/   -> algoritmo de control           (PID posicional)
    analysis/      -> métricas de desempeño          (overshoot, settling, ...)
    reporting/     -> presentación                    (ConsoleReporter)

Flujo (sin prueba y error):
  1. Respuesta al escalón en lazo abierto sobre una planta auto-regulada.
  2. Identificación FOPDT (K, tau, L) por el método de dos puntos de Smith.
  3. Predicción de ganancias con reglas analíticas.
  4. Validación a lazo cerrado: Overshoot y Settling Time.
  5. Recomendación del mejor compromiso.

Ejecutar:  python backend/models/tuning/tune_engine.py
           (es standalone: añade su propio paquete al sys.path y corre desde
            cualquier carpeta; no importa los modelos de producción).
================================================================================
"""

import os
import sys

# --- Bootstrap: poner el directorio que contiene el paquete 'tuning' en el path
# para que los imports absolutos 'tuning.*' funcionen al ejecutar como script. --
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tuning.analysis.metrics import StepResponseAnalyzer
from tuning.controllers.pid import PID
from tuning.identification.fopdt import FopdtIdentifier
from tuning.plants.pump_plant import PumpPlant
from tuning.reporting.console_reporter import ConsoleReporter
from tuning.simulation.simulator import ClosedLoopSimulation, OpenLoopStepResponse
from tuning.tuning_rules.base import Gains, TuningRule, gains_from_classic
from tuning.tuning_rules.cohen_coon import CohenCoon
from tuning.tuning_rules.ziegler_nichols import ZieglerNicholsOpenLoop

# ------------------------------------------------------------------------------
# PARÁMETROS EDITABLES  (para el flujo /tune-pid: modificar, ejecutar, analizar)
# ------------------------------------------------------------------------------

# Punto de operación del ensayo de escalón (ambos por encima de la zona muerta)
STEP_U0 = 20.0      # % de válvula inicial (régimen permanente de partida)
STEP_U1 = 50.0      # % de válvula tras el escalón
STEP_TIME = 200.0   # s de registro (debe cubrir >= 5*tau para ver el permanente)

# Consigna (setpoint) para el ensayo a lazo cerrado
SETPOINT = 1500.0   # RPM objetivo

# Opcional: ganancias manuales a comparar (None para desactivar).
MANUAL_GAINS = None   # ej: {"Kp": 0.15, "Ki": 0.03, "Kd": 0.30}


def _manual_gains_to_record(manual: dict) -> Gains:
    """Convierte el dict editable MANUAL_GAINS a un registro ``Gains``."""
    Kp = manual["Kp"]
    Ti = (Kp / manual["Ki"]) if manual.get("Ki") else 1e9
    Td = (manual.get("Kd", 0.0) / Kp) if Kp else 0.0
    return gains_from_classic(Kp, Ti, Td)


def run(plant: PumpPlant = None, rules=None, reporter: ConsoleReporter = None) -> None:
    """
    Ejecuta el flujo completo de sintonización y reporta los resultados.

    Las dependencias se inyectan (planta, reglas, reporter) para poder
    sustituirlas en pruebas o por otras implementaciones sin tocar este código.
    """
    plant = plant or PumpPlant()
    rules = rules if rules is not None else [ZieglerNicholsOpenLoop(), CohenCoon()]
    reporter = reporter or ConsoleReporter()
    analyzer = StepResponseAnalyzer()

    reporter.header(plant)

    # --- 1) Respuesta al escalón en lazo abierto -----------------------------
    step_data = OpenLoopStepResponse(plant).run(STEP_U0, STEP_U1, STEP_TIME)
    reporter.open_loop(STEP_U0, STEP_U1, step_data)

    # --- 2) Identificación FOPDT --------------------------------------------
    fit = FopdtIdentifier().identify(step_data)
    reporter.fopdt(fit, plant)

    # --- 3) Predicción de ganancias -----------------------------------------
    reporter.gains_section_title()
    candidates = []  # [(name, Gains), ...]
    for rule in rules:
        gains = rule.compute(fit.K, fit.tau, fit.L)
        candidates.append((rule.name, gains))
        reporter.gains(rule.name, gains)

    if MANUAL_GAINS:
        candidates.append(("Manual (editado)", _manual_gains_to_record(MANUAL_GAINS)))

    # --- 4) Validación a lazo cerrado ---------------------------------------
    reporter.validation_title(SETPOINT)
    results = []  # [(name, Gains, PerformanceMetrics), ...]
    for name, g in candidates:
        controller = PID(g.Kp, g.Ki, g.Kd, Ts=1.0)
        cl = ClosedLoopSimulation(plant, controller).run(SETPOINT)
        metrics = analyzer.analyze(cl.t, cl.y, setpoint=SETPOINT, x0=0.0)
        results.append((name, g, metrics))
        reporter.metrics(name, metrics)

    # --- 5) Recomendación ----------------------------------------------------
    # Criterio: penaliza sobreimpulso alto y establecimiento lento.
    best = min(results, key=lambda r: r[2].settling + 4.0 * r[2].overshoot)
    reporter.recommendation(best[0], best[1])
    reporter.warnings()


if __name__ == "__main__":
    run()
