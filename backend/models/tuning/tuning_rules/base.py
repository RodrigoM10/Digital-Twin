"""
Base abstractions for analytic tuning rules.

A ``TuningRule`` maps an identified FOPDT model (K, tau, L) to a set of PID
``Gains``. Each concrete rule is a separate, interchangeable strategy, so adding
a new method (IMC, Lambda, ...) means adding a file here — never editing the
engine (Open/Closed Principle).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Gains:
    """PID gains expressed in both parallel (Kp, Ki, Kd) and classic (Ti, Td) form."""
    Kp: float
    Ki: float
    Kd: float
    Ti: float
    Td: float


def gains_from_classic(Kp: float, Ti: float, Td: float) -> Gains:
    """Convert the classic form (Kp, Ti, Td) into a full ``Gains`` record."""
    Ki = Kp / Ti if Ti > 0 else 0.0
    Kd = Kp * Td
    return Gains(Kp=Kp, Ki=Ki, Kd=Kd, Ti=Ti, Td=Td)


class TuningRule(ABC):
    """Strategy that computes PID gains from FOPDT parameters."""

    #: Human-readable name used in reports.
    name: str = "Tuning Rule"

    @abstractmethod
    def compute(self, K: float, tau: float, L: float) -> Gains:
        """Return the PID gains for the given process parameters."""
