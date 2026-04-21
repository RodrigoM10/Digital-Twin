from core.pid_controller import ControlledUnity

class Pump:

    def __init__(self, MaxRPM):
        self.MaxRPM = MaxRPM
        self.RPM = 0 #current RPM
        
        
        self.previous = [] #necessary for the PID
    
    def update(self, update_interval):
        # Limit to 0 at max speed
        self.RPM += (-10 + (self.Valve*1.8)) * update_interval #if the valve is close, lose speed.

        if self.RPM < 10:
            self.RPM = 0
        elif self.RPM > self.MaxRPM:
            self.RPM = self.MaxRPM


class ControlledPump(Pump, ControlledUnity):
    def __init__(self, MaxRPM, kP, kI, kD):
        Pump.__init__(self, MaxRPM)
        ControlledUnity.__init__(self, kP, kI, kD)

