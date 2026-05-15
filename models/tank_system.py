import math as mt
from models.pid_controller import ControlledUnity

class Tank:
    def __init__(self, diameter=1.0, height=1.0):
        self.diameter = diameter
        self.height = height
        
        self.sensor_value = 0.0   #current tank level % (0 to 100)
        self.current_volume = 0.0  # Liters  
        self.max_volume = mt.pi * (self.diameter / 2)**2 * self.height

        self.inflow_rate = 0.0      #L/s   
        self.outflow_rate = 0.0     #Constant leak/demand L/s    
        
        self.auto_mode = True
        self.emergency_stop = False
        self.safe_stop_active = False
        self.current_step = "MONITORING"
    
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

    def emergency_stop_trigger(self):
        """Cierre inmediato de seguridad"""
        self.emergency_stop = True
        self.auto_mode = False
        self.valve = 0.0  # Cerramos entrada
        self.current_step = "EMERGENCY SHUTDOWN" 

    def display_status(self, target):
        if self.emergency_stop:
            system_mode = "EMERGENCY-TRIP"
        elif self.safe_stop_active:
            system_mode = "SHUTDOWN-SEQ"
        elif self.auto_mode:
            system_mode = "AUTO-CONTROL"
        else:
            system_mode = "MANUAL"

        print("\n" + "╔" + "═"*58 + "╗")
        print(f"║ UNIT: STORAGE TANK TK-01         MODE: {system_mode:<15} ║")
        print("╠" + "═"*28 + "╦" + "═"*29 + "╣")
        
        # Fila de Datos Analógicos
        print(f"║  LEVEL & VOLUME             ║  FLOW RATES                 ║")
        print(f"║  Level:  {self.sensor_value:>10.2f} %       ║  Inflow:  {self.inflow_rate:>8.2f} L/s   ║")
        print(f"║  Volume: {self.current_volume:>10.2f} L       ║  Outflow: {self.outflow_rate:>8.2f} L/s   ║")
        
        print("╠" + "═"*28 + "╩" + "═"*29 + "╣")
        
        bar_length = 40
        progress = int((self.sensor_value / 100) * bar_length)
        progress = max(0, min(bar_length, progress))
        
        bar = "█" * progress + "░" * (bar_length - progress)
        print(f"║ LEVEL: [{bar}] {int(self.sensor_value):>3}% ║")
        
        # Alertas y Target
        print("╠" + "═"*58 + "╣")
        status_msg = "STABLE" if abs(target - self.sensor_value) < 2 else "ADJUSTING"
        if self.emergency_stop: status_msg = "CRITICAL STOP"
        
        print(f"║  Target: {target:>10.2f} %       STATUS: {status_msg:<18} ║")
        print("╚" + "═"*58 + "╝")
        
class ControlledTank(Tank, ControlledUnity):
    def __init__(self, diameter, height, kP, kI, kD):
        Tank.__init__(self, diameter, height)
        ControlledUnity.__init__(self, kP=kP, kI=kI, kD=kD)