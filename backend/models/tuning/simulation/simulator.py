"""
Simulation engine: runs experiments on *any* plant (and controller).

This layer depends only on the ``Plant`` / ``Controller`` abstractions, so it
works unchanged with new plants or controllers (Open/Closed + Liskov).
"""

from dataclasses import dataclass
from typing import List, Tuple

from tuning.core.interfaces import Controller, Plant


@dataclass
class StepResponseData:
    """Result of an open-loop step experiment."""
    t: List[float]       # time stamps (s)
    y: List[float]       # measured output
    y0: float            # initial steady-state output
    du: float            # applied input step (u1 - u0)


@dataclass
class ClosedLoopData:
    """Result of a closed-loop simulation."""
    t: List[float]       # time stamps (s)
    y: List[float]       # process variable
    u: List[float]       # control command


class OpenLoopStepResponse:
    """Estabiliza la planta en ``u0``, aplica un escalón a ``u1`` y registra la respuesta."""

    def __init__(self, plant: Plant):
        self.plant = plant

    def run(self, u0: float, u1: float, t_total: float) -> StepResponseData:
        self.plant.reset()
        self.plant.settle(u0)
        y0 = self.plant.output

        dt = self.plant.dt
        n = int(t_total / dt)
        t, y = [], []
        clock = 0.0
        for _ in range(n):
            measurement = self.plant.step(u1)
            t.append(clock)
            y.append(measurement)
            clock += dt
        return StepResponseData(t=t, y=y, y0=y0, du=(u1 - u0))


class ClosedLoopSimulation:
    """
    Simula la planta bajo control por realimentación.

    El controlador corre a su período ``Ts`` (zero-order hold) mientras la física
    se integra al ``dt`` fino de la planta.
    """

    def __init__(self, plant: Plant, controller: Controller):
        self.plant = plant
        self.controller = controller

    def run(self, setpoint: float, t_total: float = 300.0, x0: float = 0.0) -> ClosedLoopData:
        self.plant.reset(x0)
        self.controller.reset()
        dt = self.plant.dt
        steps_per_ctrl = max(1, int(round(self.controller.Ts / dt)))

        t, y, u = [], [], []
        clock = 0.0
        command = 0.0
        pv = self.plant.output
        for k in range(int(t_total / dt)):
            if k % steps_per_ctrl == 0:
                command = self.controller.update(setpoint, pv)
            pv = self.plant.step(command)
            t.append(clock)
            y.append(pv)
            u.append(command)
            clock += dt
        return ClosedLoopData(t=t, y=y, u=u)
