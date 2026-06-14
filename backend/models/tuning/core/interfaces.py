"""
Abstract contracts (interfaces) for the PID tuning toolkit.

These ABCs are the stable core on which every other layer depends, enabling
the Dependency Inversion Principle: high-level code (the simulator, the tuning
engine) talks to ``Plant`` and ``Controller`` abstractions, never to a concrete
``PumpPlant`` or ``PID``. Concrete implementations live in ``plants/`` and
``controllers/`` and are injected by constructor.

Interfaces are kept deliberately small (Interface Segregation): a plant knows
nothing about controllers and vice versa.
"""

from abc import ABC, abstractmethod


class Plant(ABC):
    """
    A physical process that can be advanced one time step at a time.

    A plant maps a command (e.g. valve %) to a measured output (e.g. RPM),
    possibly with internal dynamics and measurement delay. Implementations must
    expose the integration step ``dt`` and the current true ``output``.
    """

    #: Fixed-step integration period in seconds. Set by the implementation.
    dt: float

    @abstractmethod
    def reset(self, output: float = 0.0) -> None:
        """Return the plant to a known initial state."""

    @abstractmethod
    def step(self, command: float) -> float:
        """Advance the physics by ``dt`` and return the (possibly delayed) measurement."""

    @property
    @abstractmethod
    def output(self) -> float:
        """Current *true* (non-delayed) output of the plant."""

    def settle(self, command: float, t: float = 400.0) -> float:
        """
        Drive the plant to steady state for a constant ``command``.

        Default implementation simply integrates forward for ``t`` seconds.
        Plants with measurement delay should override to also realign their
        delay buffers with the steady value.
        """
        for _ in range(int(t / self.dt)):
            self.step(command)
        return self.output


class Controller(ABC):
    """
    A feedback controller that computes a command from a setpoint and a
    process variable (measurement).
    """

    #: Control sampling period in seconds (zero-order hold).
    Ts: float

    @abstractmethod
    def reset(self) -> None:
        """Clear internal controller state (integrators, history, ...)."""

    @abstractmethod
    def update(self, setpoint: float, pv: float) -> float:
        """Return the control command for the given setpoint and process variable."""
