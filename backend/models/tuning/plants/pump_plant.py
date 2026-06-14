"""
Self-regulating pump plant model used for FOPDT identification and validation.

This is the *physics* layer: it owns the differential equation of the equipment
and knows nothing about controllers, tuning rules or metrics.
"""

from tuning.core.interfaces import Plant


class PumpPlant(Plant):
    """
    First-order pump model with viscous/aerodynamic load and measurement delay.

        J * d(omega)/dt = b*valve - d*omega - bias

      =>  tau = J/d        (time constant)
          K   = b/d        (static gain, RPM per % of valve)
          omega_ss(valve) = (b*valve - bias) / d

    Unlike the pure-integrator production models (pump/tank/turbine), the load
    term ``-d*omega`` makes this plant *self-regulating*: a step input produces
    an S-shaped reaction curve that settles at a new steady state, which is what
    the classic FOPDT identification methods require.

    A transport/measurement delay ``L`` (sensor + piping) is modelled as a FIFO
    buffer on the measured signal.

    Defaults -> tau = 1.0/0.05 = 20 s, K = 1.8/0.05 = 36 RPM/%, L = 3 s.
    (``b`` and ``bias`` inherit the production coefficients; ``-d*omega`` is the
    realistic load term the production model omits.)
    """

    def __init__(self, b=1.8, d=0.05, J=1.0, bias=10.0, dead_time=3.0,
                 v_min=0.0, v_max=100.0, dt=0.05):
        self.b, self.d, self.J, self.bias = b, d, J, bias
        self.v_min, self.v_max = v_min, v_max
        self.dt = dt
        self.dead_time = dead_time
        self._delay_n = max(1, int(round(dead_time / dt)))
        self.reset()

    # --- True process parameters (ground truth for validating the fit) --------
    @property
    def tau_true(self) -> float:
        """True time constant tau = J / d."""
        return self.J / self.d

    @property
    def gain_true(self) -> float:
        """True static gain K = b / d (RPM per % valve)."""
        return self.b / self.d

    def steady_state(self, valve: float) -> float:
        """Analytic steady-state speed for a constant valve opening."""
        return max(0.0, (self.b * valve - self.bias) / self.d)

    # --- Plant interface ------------------------------------------------------
    @property
    def output(self) -> float:
        return self.speed

    def reset(self, output: float = 0.0) -> None:
        self.speed = output
        self._buf = [output] * self._delay_n   # measurement-delay buffer

    def step(self, command: float) -> float:
        """Advance the physics one ``dt`` and return the delayed measurement."""
        valve = min(self.v_max, max(self.v_min, command))
        domega = (self.b * valve - self.d * self.speed - self.bias) / self.J
        self.speed += domega * self.dt
        if self.speed < 0.0:
            self.speed = 0.0
        self._buf.append(self.speed)
        return self._buf.pop(0)

    def settle(self, command: float, t: float = 400.0) -> float:
        """Settle to steady state and realign the delay buffer with it."""
        super().settle(command, t)
        self._buf = [self.speed] * self._delay_n
        return self.speed
