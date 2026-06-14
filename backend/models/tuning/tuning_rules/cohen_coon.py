"""Cohen-Coon tuning rule."""

from tuning.tuning_rules.base import Gains, TuningRule, gains_from_classic


class CohenCoon(TuningRule):
    """
    Cohen-Coon, controlador PID.

        r  = L / tau
        Kp = (tau / (K * L)) * (4/3 + r/4)
        Ti = L * (32 + 6r) / (13 + 8r)
        Td = L * 4 / (11 + 2r)

    Mejor desempeño que Ziegler-Nichols cuando el tiempo muerto es alto.
    """

    name = "Cohen-Coon"

    def compute(self, K: float, tau: float, L: float) -> Gains:
        r = L / tau
        Kp = (tau / (K * L)) * (4.0 / 3.0 + r / 4.0)
        Ti = L * (32.0 + 6.0 * r) / (13.0 + 8.0 * r)
        Td = L * 4.0 / (11.0 + 2.0 * r)
        return gains_from_classic(Kp, Ti, Td)
