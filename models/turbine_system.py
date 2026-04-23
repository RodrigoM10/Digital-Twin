import time
import threading
from core.pid_controller import ControlledUnity

class Turbine:
    def __init__(self):
        # Physical States
        self.RPM = 0.0
        self.temperature = 0.0
        self.pressure = 0.0
        self.friction = 5.0
        self.sensor_value = 0.0 # Will be linked to RPM
        
        # Digital I/O
        self.aux_motor = False
        self.pneumatic_joint = False
        self.igniters = False
        self.burners_on = False
        self.emergency_stop = False
        
        # Internal control
        self.auto_mode = False
        self.valve = 0.0 # From PID

    def update(self, delta_time=0.1):
        # Physics Logic
        motor_contribution = 10.0 if (self.aux_motor and self.pneumatic_joint) else 0.0
        burner_contribution = self.valve * 0.8 if self.burners_on else 0.0
        
        # Acceleration formula
        acceleration = (motor_contribution + burner_contribution - self.friction)
        self.RPM += acceleration * (delta_time * 10) # Scaled for 0.1s updates
        
        if self.RPM < 0: 
            self.RPM = 0
            print('Failed to boot, check input values.')

        self.sensor_value = self.RPM

    def run_startup_sequence(self):
        """Sequence of startup handled in a background thread"""
        def sequence():
            print("\n[SYSTEM] Starting Aux Motor and Pneumatic Joint...")
            self.aux_motor = True
            self.pneumatic_joint = True
            
            # Wait for self-sustained speed
            while self.RPM < 478: time.sleep(0.1)
            
            print(f"\n[SYSTEM] Self-Sustain Speed Reached ({round(self.RPM)} RPM). Enabling Igniters...")
            self.igniters = True
            time.sleep(1)
            self.burners_on = True
            print("[SYSTEM] Burners ON. Switching to Manual Valve Control...")
            
            # Wait for decouple speed
            while self.RPM < 2750: time.sleep(0.1)
            
            print(f"\n[SYSTEM] Decouple Speed Reached ({round(self.RPM)} RPM). Turning off Aux Motor...")
            self.pneumatic_joint = False
            time.sleep(2)
            self.aux_motor = False
            self.auto_mode = True
            print("[SYSTEM] Aux Motor OFF. PID Auto-Mode ENGAGED.")

        thread = threading.Thread(target=sequence, daemon=True)
        thread.start()

    def display_status(self, target):
        status = "AUTO" if self.auto_mode else "MANUAL/STARTUP"
        print(f"\n" + "="*40)
        print(f" TURBINE STATUS: {status} ")
        print(f"="*40)
        print(f"RPM:            {self.RPM:>8.2f}")
        print(f"Target RPM:     {target:>8.2f}")
        print(f"Valve Position: {self.valve:>8.2f} %")
        print(f"Aux Motor:      {'ON' if self.aux_motor else 'OFF'}")
        print(f"Burners:        {'READY' if self.burners_on else 'OFF'}")
        print(f"-"*40)

class ControlledTurbine(Turbine, ControlledUnity):
    def __init__(self, kP, kI, kD):
        Turbine.__init__(self)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)
        # Start the sequence automatically upon creation
        self.run_startup_sequence()