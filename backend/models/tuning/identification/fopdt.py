"""
FOPDT process identification from an open-loop reaction curve.

Turns measured step-response data into a First-Order-Plus-Dead-Time model
(K, tau, L). Depends only on raw signals, so it is independent of how the data
was produced.
"""

from dataclasses import dataclass

from tuning.core.signal_utils import first_crossing_time
from tuning.simulation.simulator import StepResponseData


@dataclass
class FopdtModel:
    """Identified First-Order-Plus-Dead-Time parameters."""
    K: float        # static gain (RPM / %)
    tau: float      # time constant (s)
    L: float        # apparent dead time (s)
    y_inf: float    # final steady-state output
    y_0: float      # initial steady-state output


class FopdtIdentifier:
    """
    Identifica K, tau, L con el método de dos puntos de Smith (28.3% / 63.2%).

      K   = (y_inf - y0) / du                      (static gain)
      tau = 1.5 * (t63.2 - t28.3)                  (Smith two-point method)
      L   = t63.2 - tau                            (apparent dead time)
    """

    def __init__(self, tail_samples: int = 20):
        #: number of trailing samples averaged to estimate the new steady state
        self.tail_samples = tail_samples

    def identify(self, data: StepResponseData) -> FopdtModel:
        y, t = data.y, data.t
        y0, du = data.y0, data.du

        y_inf = sum(y[-self.tail_samples:]) / self.tail_samples
        dy = y_inf - y0
        if abs(dy) < 1e-9 or abs(du) < 1e-9:
            raise ValueError("Respuesta plana: no se puede identificar (revisar escalón).")

        K = dy / du
        t283 = first_crossing_time(t, y, y0 + 0.283 * dy)
        t632 = first_crossing_time(t, y, y0 + 0.632 * dy)
        tau = 1.5 * (t632 - t283)
        L = t632 - tau
        if L < 0.0:
            L = max(1e-3, t283 - tau / 3.0)   # numerical safeguard
        return FopdtModel(K=K, tau=tau, L=L, y_inf=y_inf, y_0=y0)
