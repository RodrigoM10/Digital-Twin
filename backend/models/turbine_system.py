import time
import threading
from models.pid_controller import ControlledUnity

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

        self.startup_sequence = False
        self.emergency_stop = False
        self.safe_stop = False
        
        # Internal control
        self.auto_mode = False
        self.valve = 0.0 # From PID

        self.current_step = "STAND BY"

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
            self.startup_sequence = True
            self.current_step = "1. CRANKING (AUX MOTOR)"
            self.aux_motor = True
            self.pneumatic_joint = True
            
            # Wait for self-sustained speed
            while self.RPM < 478: time.sleep(0.1)
            
            self.current_step = "2. IGNITION PHASE"
            self.igniters = True
            time.sleep(1)
            self.burners_on = True
            
            # Wait for decouple speed
            while self.RPM < 2750: time.sleep(0.1)
            
            self.current_step = "3. DECOUPLING AUX MOTOR"
            self.pneumatic_joint = False
            time.sleep(2)
            self.aux_motor = False

            self.current_step = "4. PID Auto-Mode ENGAGED"
            self.startup_sequence = False
            self.auto_mode = True
           

        thread = threading.Thread(target=sequence, daemon=True)
        thread.start()
    
    def stop_sequence(self):
        def sequence():
            self.safe_stop = True
            self.auto_mode = False  # TO MANUAL
            self.current_step = "SHUTDOWN: REDUCING SPEED"
            
            self.valve = 10.0
            time.sleep(10)
            
            self.current_step = "SHUTDOWN: CUTTING FUEL"
            self.burners_on = False
            self.igniters = False
            self.valve = 0.0
            
            self.current_step = "SHUTDOWN: COOLING DOWN"

            while self.RPM > 800:
                time.sleep(0.5)
            
            if self.RPM == 0.0 :
                self.current_step = "SYSTEM STOPPED"
                print("\n[INFO] Safe shutdown completed.")

        threading.Thread(target=sequence, daemon=True).start()

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

class ControlledTurbine(Turbine, ControlledUnity):
    def __init__(self, kP, kI, kD):
        Turbine.__init__(self)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)
        # Start the sequence automatically upon creation
        self.run_startup_sequence()