"""
Standard positional PID controller used for closed-loop validation.

This is the *control algorithm* layer. It is completely decoupled from any
physical model: it only sees a setpoint and a process variable, and returns a
command. The same controller can drive any object implementing ``Plant``.
"""

from tuning.core.interfaces import Controller


class PID(Controller):
    """
    Discrete positional PID:  u = Kp*e + Ki*∫e dt + Kd*de/dt

    with output saturation and anti-windup via *conditional integration*: the
    integrator only accumulates when the output is not saturated, or when the
    error pushes the output back out of saturation. This prevents the integrator
    from "charging up" during transients.
    """

    def __init__(self, Kp, Ki, Kd, Ts=1.0, out_min=0.0, out_max=100.0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.Ts = Ts
        self.out_min, self.out_max = out_min, out_max
        self.reset()

    def reset(self) -> None:
        self.integral = 0.0
        self.prev_e = None

    def update(self, setpoint: float, pv: float) -> float:
        e = setpoint - pv
        p = self.Kp * e
        d = 0.0 if self.prev_e is None else self.Kd * (e - self.prev_e) / self.Ts

        u_unsat = p + self.integral + d
        u = min(self.out_max, max(self.out_min, u_unsat))

        # Conditional-integration anti-windup: skip integration while saturated
        # in the direction the error would worsen.
        saturated_high = u_unsat > self.out_max and e > 0
        saturated_low = u_unsat < self.out_min and e < 0
        if not (saturated_high or saturated_low):
            self.integral += self.Ki * e * self.Ts

        self.prev_e = e
        return u
