"""
Closed-loop performance metrics for a step response.

Pure analysis layer: given time/output arrays and a setpoint, compute the
classic control-quality indicators.
"""

from dataclasses import dataclass
from typing import Sequence

from tuning.core.signal_utils import first_crossing_time


@dataclass
class PerformanceMetrics:
    """Step-response quality indicators."""
    overshoot: float    # %
    settling: float     # settling time within ±2% band (s)
    rise: float         # 10%-90% rise time (s)
    peak: float         # maximum output
    sse: float          # steady-state error (setpoint - y_final)
    y_final: float      # final averaged output


class StepResponseAnalyzer:
    """Computes overshoot, settling time, rise time and steady-state error."""

    def __init__(self, settling_band: float = 0.02, tail_samples: int = 20):
        self.settling_band = settling_band      # fraction of setpoint (±2% default)
        self.tail_samples = tail_samples

    def analyze(self, t: Sequence[float], y: Sequence[float],
                setpoint: float, x0: float = 0.0) -> PerformanceMetrics:
        peak = max(y)
        overshoot = max(0.0, (peak - setpoint) / setpoint * 100.0) if setpoint else 0.0

        # Settling time: last instant outside the ±band of the setpoint.
        band = self.settling_band * abs(setpoint)
        settling = 0.0
        for i in range(len(y) - 1, -1, -1):
            if abs(y[i] - setpoint) > band:
                settling = t[i]
                break

        # Rise time over 10% -> 90% of the total travel.
        span = setpoint - x0
        t10 = first_crossing_time(t, y, x0 + 0.10 * span)
        t90 = first_crossing_time(t, y, x0 + 0.90 * span)
        rise = max(0.0, t90 - t10)

        y_final = sum(y[-self.tail_samples:]) / self.tail_samples
        sse = setpoint - y_final
        return PerformanceMetrics(overshoot=overshoot, settling=settling, rise=rise,
                                  peak=peak, sse=sse, y_final=y_final)
