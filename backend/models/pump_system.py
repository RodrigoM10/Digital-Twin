from backend.models.pid_controller import ControlledUnity

class Pump:

    def __init__(self, MaxRPM):
        self.MaxRPM = MaxRPM
        self.sensor_value = 0 #current Pump Speed RPM RPM


        # Atributos para el Panel
        self.auto_mode = True
        self.emergency_stop = False
        self.current_step = "READY"
    
    def update(self, update_interval):
        # Limit to 0 at max speed
        self.sensor_value += (-10 + (self.valve*1.8)) * update_interval #if the valve is close, lose speed.

        if self.sensor_value < 10:
            self.sensor_value = 0
        elif self.sensor_value > self.MaxRPM:
            self.sensor_value = self.MaxRPM
        
        self.current_step = "CONTROL ACTIVE"

    def emergency_stop_trigger(self):
        self.auto_mode = False
        self.emergency_stop = True
        self.valve = 0.0
        self.current_step = "EMERGENCY TRIP ACTIVATED"

    
    def display_status(self, target):
  
        if getattr(self, 'emergency_stop', False):
            system_mode = "EMERGENCY-TRIP   "
            status_text = "CRITICAL: STOPPED"
        elif not getattr(self, 'auto_mode', True):
            system_mode = "MANUAL-STOP      "
            status_text = "SYSTEM READY     "
        else:
            system_mode = "AUTO-CONTROL     "
            status_text = "STABLE           " if abs(target - self.sensor_value) < 5 else "ADJUSTING        "

        print("\n" + "╔" + "═"*60 + "╗")
        print(f"║ UNIT: HYDRAULIC PUMP AX-100      MODE: {system_mode:<15}   ║")
        print("╠" + "═"*60 + "╣")
        
        print(f"║  ANALOG SENSORS             ║  CONTROL STATUS              ║")
        print(f"║  Speed:  {self.sensor_value:>10.2f} RPM     ║  Target: {target:>10.2f} RPM      ║")
        print(f"║  Valve:  {self.valve:>10.2f} %       ║  Status: {status_text:<15}   ║")
        
        print("╠" + "═"*60 + "╣")
        
        bar_length = 40
        max_rpm_gauge = 4000 
        progress = int((self.sensor_value / max_rpm_gauge) * bar_length)
        progress = max(0, min(bar_length, progress)) # Evita errores de dibujo
        bar = "█" * progress + "░" * (bar_length - progress)
        
        print(f"║ YIELD:  [{bar}] {int((self.sensor_value/max_rpm_gauge)*100):>3}%    ║")
        print(f"║ MAX RPM LIMIT:  4000 rpm                                   ║")
        
        # Alertas
        if getattr(self, 'emergency_stop', False):
            print("║ ALERT: [ EMERGENCY STOP ACTIVATED - CHECK SYSTEM ]         ║")
        else:
            print(f"║ MSG: {getattr(self, 'current_step', 'SYSTEM RUNNING'):<50}    ║")
            
        print("╚" + "═"*60 + "╝")

class ControlledPump(Pump, ControlledUnity):
    def __init__(self, MaxRPM, kP, kI, kD):
        Pump.__init__(self, MaxRPM)
        ControlledUnity.__init__(self, kP, kI, kD)

