"""
Small, dependency-free numeric helpers shared across layers.

Lives in ``core`` so that both ``identification`` and ``analysis`` can depend on
it without depending on each other (keeping the dependency graph acyclic).
"""

from typing import Sequence


def first_crossing_time(t: Sequence[float], y: Sequence[float], level: float) -> float:
    """
    First instant (linearly interpolated) at which signal ``y`` crosses ``level``.

    Returns the last timestamp if the level is never crossed.
    """
    for i in range(1, len(y)):
        a, b = y[i - 1], y[i]
        if (a - level) * (b - level) <= 0 and b != a:
            frac = (level - a) / (b - a)
            return t[i - 1] + frac * (t[i] - t[i - 1])
    return t[-1]
