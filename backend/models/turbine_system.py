import time
import threading
from backend.models.pid_controller import ControlledUnity

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

    def display_status(self, target):
    
        def led(state): return "[ ON  ]" if state else "[ OFF ]"
        
        system_mode = "------" 
        if self.RPM == 0.0:
            system_mode = "STOP"
        elif self.auto_mode:
            system_mode = "AUTO-CONTROL"
        elif self.safe_stop: 
            system_mode = "SHUTDOWN-SEQ"
        elif self.emergency_stop:
            system_mode = "EMERGENCY-TRIP"
        elif self.startup_sequence:
            system_mode = "SEQUENCE-STARTUP"
        else: 
            pass

        # Panel Control
        print("\n" + "╔" + "═"*58 + "╗")
        print(f"║ UNIT: GAS TURBINE GEN-3         MODE: {system_mode:<15} ║")
        print("╠" + "═"*28 + "╦" + "═"*29 + "╣")
        if self.RPM == 0.0:
         print(f"║ STEP: ---------- ║")
        else:
         print(f"║ STEP: {self.current_step:<45} ║")
        print(f"║ MAX RPM: {1200} ║")

        # Fila 1: Main Sensor
        print(f"║  ANALOG SENSORS             ║  DIGITAL INDICATORS         ║")
        print(f"║  RPM:    {self.RPM:>10.2f}         ║  Aux Motor:    {led(self.aux_motor)}      ║")
        print(f"║  Target: {target:>10.2f}         ║  Pneum. Joint: {led(self.pneumatic_joint)}      ║")
        
        # Fila 2: Combustion
        print(f"║  Valve:  {self.valve:>10.2f} %       ║  Igniters:     {led(self.igniters)}      ║")
        print(f"║  MAX RPM:   {12000.00}         ║  Burners:      {led(self.burners_on)}      ║")
        #print(f"║  Temp:   {self.temperature:>10.2f} °C      ║  Burners:      {led(self.burners_on)}      ║")
        
        print("╠" + "═"*58 + "╣")
        
        # Progress Bar
        bar_length = 40
        progress = int((self.RPM / 12000) * bar_length) # 12000 RPM max
        bar = "█" * progress + "░" * (bar_length - progress)
        print(f"║ SPEED: [{bar}] {int((self.RPM/12000)*100):>3}% ║")
        
        # Security Alert
        if self.RPM == 0.0:
            print("║ ALERT: [ System STOP ]                               ║")
        elif self.safe_stop:
            print("║ ALERT: [ SAFE STOP ACTIVATED ]                         ║")
        elif self.RPM > target:
            print("║ ALERT: [ OVER-SPEED WARNING ]                               ║")
        if self.emergency_stop:
            print("║ ALERT: [ EMERGENCY STOP ACTIVATED ]                         ║")
        else:
            print("║ STATUS: [ SYSTEM OPERATING NORMALLY ]                       ║")
            
        print("╚" + "═"*58 + "╝")
    

class ControlledTurbine(Turbine, ControlledUnity):
    def __init__(self, kP, kI, kD):
        Turbine.__init__(self)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)
        # Start the sequence automatically upon creation
        self.run_startup_sequence()