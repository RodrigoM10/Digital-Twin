"""Reglas analíticas de sintonización."""

from tuning.tuning_rules.base import Gains, TuningRule, gains_from_classic
from tuning.tuning_rules.cohen_coon import CohenCoon
from tuning.tuning_rules.ziegler_nichols import ZieglerNicholsOpenLoop

__all__ = [
    "TuningRule",
    "Gains",
    "gains_from_classic",
    "ZieglerNicholsOpenLoop",
    "CohenCoon",
]
