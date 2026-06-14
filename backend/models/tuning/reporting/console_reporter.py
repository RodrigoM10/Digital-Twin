"""
Console presentation layer.

Isolates *all* console output from the computation. Swapping this for a JSON or
HTML reporter would not touch any other module (Single Responsibility +
Dependency Inversion: the engine talks to a reporter object).
"""

from tuning.analysis.metrics import PerformanceMetrics
from tuning.identification.fopdt import FopdtModel
from tuning.plants.pump_plant import PumpPlant
from tuning.simulation.simulator import StepResponseData
from tuning.tuning_rules.base import Gains


class ConsoleReporter:
    """Renders the tuning report to stdout."""

    def header(self, plant: PumpPlant) -> None:
        print("=" * 78)
        print(" PID SANDBOX - Identificacion FOPDT + Sintonizacion analitica")
        print("=" * 78)
        print("\n[PLANTA] Bomba con carga.  Valores fisicos REALES del modelo:")
        print(f"         K_real = {plant.gain_true:.2f} RPM/%   "
              f"tau_real = {plant.tau_true:.2f} s   L_real = {plant.dead_time:.2f} s")

    def open_loop(self, u0: float, u1: float, data: StepResponseData) -> None:
        print(f"\n[1] RESPUESTA AL ESCALON EN LAZO ABIERTO  "
              f"({u0:.0f}% -> {u1:.0f}% de valvula)")
        print(f"    y0 (permanente inicial) = {data.y0:.1f} RPM   ->   "
              f"y_inf (permanente final) = {data.y[-1]:.1f} RPM   "
              f"(delta_u = {data.du:.0f}%)")

    def fopdt(self, fit: FopdtModel, plant: PumpPlant) -> None:
        print("\n[2] PARAMETROS FOPDT IDENTIFICADOS (metodo de Smith 28.3/63.2%)")
        print(f"    K   = {fit.K:.3f} RPM/%     (real {plant.gain_true:.3f})")
        print(f"    tau = {fit.tau:.3f} s        (real {plant.tau_true:.3f})")
        print(f"    L   = {fit.L:.3f} s         (real {plant.dead_time:.3f})")

    def gains_section_title(self) -> None:
        print("\n[3] GANANCIAS PREDICHAS (analiticas, sin prueba y error)")

    def gains(self, name: str, g: Gains) -> None:
        print(f"  {name:<16} Kp = {g.Kp:>8.4f}   Ki = {g.Ki:>8.4f}   "
              f"Kd = {g.Kd:>8.4f}   (Ti={g.Ti:.2f}s, Td={g.Td:.2f}s)")

    def validation_title(self, setpoint: float) -> None:
        print(f"\n[4] VALIDACION A LAZO CERRADO  (setpoint = {setpoint:.0f} RPM)")

    def metrics(self, name: str, m: PerformanceMetrics) -> None:
        print(f"  {name:<16} Overshoot = {m.overshoot:>6.2f}%   "
              f"Settling(±2%) = {m.settling:>7.2f}s   "
              f"Rise = {m.rise:>6.2f}s   SSE = {m.sse:>7.2f} RPM")

    def recommendation(self, best_name: str, g: Gains) -> None:
        print("\n[5] RECOMENDACION")
        print(f"    Mejor compromiso overshoot/settling -> '{best_name}'")
        self.gains("   ->", g)

    def warnings(self) -> None:
        print("\n" + "-" * 78)
        print(" AVISOS antes de llevar a produccion:")
        print("  * El PID de produccion (models/pid_controller.py) NO es posicional:")
        print("    usa forma incremental (Output = valve + aP + aI + aD), asi que")
        print("    estas ganancias son un PUNTO DE PARTIDA, no transfieren 1:1.")
        print("  * ZN suele dar ~20-30% de sobreimpulso; si se requiere respuesta")
        print("    suave, detunear multiplicando Kp por ~0.5 (regla practica).")
        print("  * El modelo de produccion es integrador puro (sin carga -d*omega);")
        print("    revalidar con el lazo real antes de fijar valores.")
        print("=" * 78)
