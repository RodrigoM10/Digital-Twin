from core.pid_controller import ControlledUnity

class Pump:

    def __init__(self, MaxRPM):
        self.MaxRPM = MaxRPM
        self.sensor_value = 0 #current Pump Speed RPM RPM
        
        self.current_step = "STAND BY"
    
    def update(self, update_interval):
        # Limit to 0 at max speed
        self.sensor_value += (-10 + (self.valve*1.8)) * update_interval #if the valve is close, lose speed.

        if self.sensor_value < 10:
            self.sensor_value = 0
        elif self.sensor_value > self.MaxRPM:
            self.sensor_value = self.MaxRPM
        
        self.current_step = "CONTROL ACTIVE"

    def emergency_stop_trigger(self):
        self.valve = 0.0
        self.current_step = "EMERGENCY TRIP ACTIVATED"

    def display_status(self, target):
        print(f"\n" + "="*30)
        print(f" PUMP SYSTEM STATUS ")
        print(f"="*30)
        print(f"CURRENT STEP: {self.current_step}")

        print(f"Target Speed:  {target:>8.2f} RPM")
        print(f"Current Speed: {self.sensor_value:>8.2f} RPM")
        print(f"valve Opening: {self.valve:>8.2f} %")
        print(f"Status:        {'STABLE' if abs(target - self.sensor_value) < 5 else 'ADJUSTING'}")


class ControlledPump(Pump, ControlledUnity):
    def __init__(self, MaxRPM, kP, kI, kD):
        Pump.__init__(self, MaxRPM)
        ControlledUnity.__init__(self, kP, kI, kD)

