import math as mt
from core.pid_controller import ControlledUnity

class Tank:
    def __init__(self, diameter=1.0, height=1.0):
        self.diameter = diameter
        self.height = height
        
        self.sensor_value = 0.0   #current tank level % (0 to 100)
        self.current_volume = 0.0  # Liters  
        self.max_volume = mt.pi * (self.diameter / 2)**2 * self.height

        self.inflow_rate = 0.0      #L/s   
        self.outflow_rate = 0.0     #Constant leak/demand L/s    
            
    
    def update(self, delta_time=1.0):

        max_flow = 3.0
        out_valve_pos = 20.0

        self.inflow_rate = (self.valve / 100) * max_flow

        self.outflow_rate = (out_valve_pos / 100) * max_flow

        net_flow = self.inflow_rate - self.outflow_rate
        
        self.current_volume += net_flow * delta_time

        # Physical constraints (Cannot be negative or overflow)
        if self.current_volume < 0:
            self.current_volume = 0
        elif self.current_volume > self.max_volume:
            self.current_volume = self.max_volume
        
        self.sensor_value = (self.current_volume / self.max_volume) * 100
        
    
    def display_status(self, target):
        print(f"\n" + "-"*40)
        print(f" TANK DIGITAL TWIN DATA ")
        print(f"-"*40)
        print(f"Inflow (valve E):  {self.inflow_rate:>8.2f} L/s")
        print(f"Outflow (Leak S):  {self.outflow_rate:>8.2f} L/s")
        print(f"Current Volume:    {self.current_volume:>8.2f} L")
        print(f"Max Volume:        {self.max_volume:>8.2f} L")
        print(f"Current Level:     {self.sensor_value:>8.2f} %")
        print(f"Target Level:      {target:>8.2f}  %")
        print(f"Status:            {'STABLE' if abs(target - self.sensor_value) < 5 else 'ADJUSTING'}")

class ControlledTank(Tank, ControlledUnity):
    def __init__(self, diameter, height, kP, kI, kD):
        Tank.__init__(self, diameter, height)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)