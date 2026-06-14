from models.pid_controller import ControlledUnity

# Factor de escala de tiempo de la simulacion.
# El lazo de telemetria avanza la fisica con update(delta_time) en cada tick.
# Con este factor, 1 s real de polling equivale a 10 s simulados, de modo que
# el arranque de la turbina se ve en ~10 s en el demo en lugar de minutos.
SIM_TIME_SCALE = 10.0


class Turbine:
    def __init__(self):
        # Physical States
        self.RPM = 0.0
        self.temperature = 0.0
        self.pressure = 0.0
        self.friction = 5.0
        self.sensor_value = 0.0  # Will be linked to RPM

        # Digital I/O
        self.aux_motor = False
        self.pneumatic_joint = False
        self.igniters = False
        self.burners_on = False

        self.startup_sequence = False
        self.emergency_stop = False
        self.safe_stop = False

        # Internal control
        self.auto_mode = False
        self.valve = 0.0  # From PID

        self.current_step = "STAND BY"

        # --- Maquinas de estado de arranque / parada -----------------------
        # En vez de hilos con time.sleep() + busy-wait sobre la RPM (que
        # dependian de que el frontend siguiera polleando para que la fisica
        # avanzara), las secuencias se evaluan paso a paso dentro de update().
        # Asi la fisica y la logica de secuencia avanzan acopladas al mismo
        # delta_time, sin hilos ni esperas activas.
        self._startup_phase = 0
        self._shutdown_phase = 0
        self._shutdown_active = False
        self._phase_timer = 0.0  # segundos reales acumulados en la fase actual

    # ----------------------------------------------------------------------
    # FISICA
    # ----------------------------------------------------------------------
    def update(self, delta_time=1.0):
        # Avanza las secuencias de arranque/parada (si estan activas) usando
        # el mismo delta_time que la fisica.
        if self.startup_sequence:
            self._advance_startup(delta_time)
        elif self._shutdown_active:
            self._advance_shutdown(delta_time)

        # Physics Logic
        motor_contribution = 10.0 if (self.aux_motor and self.pneumatic_joint) else 0.0
        burner_contribution = self.valve * 0.8 if self.burners_on else 0.0

        # Acceleration formula
        acceleration = (motor_contribution + burner_contribution - self.friction)
        self.RPM += acceleration * delta_time * SIM_TIME_SCALE

        if self.RPM < 0:
            self.RPM = 0
            print('Failed to boot, check input values.')

        self.sensor_value = self.RPM

    # ----------------------------------------------------------------------
    # SECUENCIA DE ARRANQUE (maquina de estados)
    # ----------------------------------------------------------------------
    def run_startup_sequence(self):
        """Inicia la secuencia de arranque. Avanza dentro de update()."""
        self.startup_sequence = True
        self._shutdown_active = False
        self._startup_phase = 0
        self._phase_timer = 0.0

    def _advance_startup(self, delta_time):
        if self._startup_phase == 0:
            # 1. Cranking con motor auxiliar hasta velocidad autosostenida
            self.current_step = "1. CRANKING (AUX MOTOR)"
            self.aux_motor = True
            self.pneumatic_joint = True
            if self.RPM >= 478:
                self.igniters = True
                self.current_step = "2. IGNITION PHASE"
                self._startup_phase = 1
                self._phase_timer = 0.0

        elif self._startup_phase == 1:
            # Espera de ignicion (~1 s) antes de encender quemadores
            self._phase_timer += delta_time
            if self._phase_timer >= 1.0:
                self.burners_on = True
                self._startup_phase = 2

        elif self._startup_phase == 2:
            # Acelerando hasta velocidad de desacople
            if self.RPM >= 2750:
                self.current_step = "3. DECOUPLING AUX MOTOR"
                self.pneumatic_joint = False
                self._startup_phase = 3
                self._phase_timer = 0.0

        elif self._startup_phase == 3:
            # Desacople del motor auxiliar (~2 s)
            self._phase_timer += delta_time
            if self._phase_timer >= 2.0:
                self.aux_motor = False
                self.current_step = "4. PID Auto-Mode ENGAGED"
                self.auto_mode = True
                self.startup_sequence = False
                self._startup_phase = 4

    # ----------------------------------------------------------------------
    # SECUENCIA DE PARADA SEGURA (maquina de estados)
    # ----------------------------------------------------------------------
    def stop_sequence(self):
        """Inicia la parada segura. Avanza dentro de update()."""
        self.safe_stop = True
        self.auto_mode = False
        self.startup_sequence = False
        self._shutdown_active = True
        self._shutdown_phase = 0
        self._phase_timer = 0.0

    def _advance_shutdown(self, delta_time):
        if self._shutdown_phase == 0:
            # Reduce velocidad con valvula minima durante ~10 s
            self.current_step = "SHUTDOWN: REDUCING SPEED"
            self.valve = 10.0
            self._phase_timer += delta_time
            if self._phase_timer >= 10.0:
                self._shutdown_phase = 1

        elif self._shutdown_phase == 1:
            # Corta combustible
            self.current_step = "SHUTDOWN: CUTTING FUEL"
            self.burners_on = False
            self.igniters = False
            self.valve = 0.0
            self._shutdown_phase = 2

        elif self._shutdown_phase == 2:
            # Enfriamiento por inercia hasta detenerse
            self.current_step = "SHUTDOWN: COOLING DOWN"
            if self.RPM <= 0:
                self.current_step = "SYSTEM STOPPED"
                self.safe_stop = False
                self._shutdown_active = False
                self._shutdown_phase = 3
                print("\n[INFO] Safe shutdown completed.")

    def emergency_stop_trigger(self):
        self.emergency_stop = True
        self.safe_stop = False
        self.auto_mode = False
        self.burners_on = False
        self.igniters = False
        self.aux_motor = False
        self.pneumatic_joint = False
        self.valve = 0.0
        self.friction = 20
        self.current_step = "EMERGENCY TRIP ACTIVATED"
        # Cancela cualquier secuencia en curso
        self.startup_sequence = False
        self._shutdown_active = False


class ControlledTurbine(Turbine, ControlledUnity):
    def __init__(self, kP, kI, kD):
        Turbine.__init__(self)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)
        # Start the sequence automatically upon creation
        self.run_startup_sequence()
