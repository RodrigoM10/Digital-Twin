"""Ziegler-Nichols open-loop (reaction-curve) tuning rule."""

from tuning.tuning_rules.base import Gains, TuningRule, gains_from_classic


class ZieglerNicholsOpenLoop(TuningRule):
    """
    Ziegler-Nichols por curva de reacción (lazo abierto), controlador PID.

        Kp = 1.2 * tau / (K * L)
        Ti = 2.0 * L
        Td = 0.5 * L

    Tiende a respuestas agresivas (~20-30% de sobreimpulso).
    """

    name = "Ziegler-Nichols"

    def compute(self, K: float, tau: float, L: float) -> Gains:
        Kp = 1.2 * tau / (K * L)
        Ti = 2.0 * L
        Td = 0.5 * L
        return gains_from_classic(Kp, Ti, Td)
