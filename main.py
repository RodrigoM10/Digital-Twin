import time
import os
import sys
import msvcrt

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from models.pump_system import ControlledPump
from models.tank_system import ControlledTank
from models.turbine_system import ControlledTurbine

def select_equipment():
    equipment = {
        "1": {"name": "Pump (RPM)", 
              "class": ControlledPump, 
              "params": {"MaxRPM": 4000,
                         "kP":10.0, 
                         "kI":0.0001, 
                         "kD":0.01}},
        "2": {
            "name": "Water Tank (Level %)",
            "class": ControlledTank,
            "params": {
                "diameter": 2.0, 
                "height": 10.0, 
                "kP": 12.0,
                "kI": 0.05, 
                "kD": 0.2
            }},
        "3": {
            "name": "Gas Turbine (RPM)",
            "class": ControlledTurbine,
            "params": {
                "kP": 0.8, 
                "kI": 0.05, 
                "kD": 0.1
            }} 
        }
    print("\n=== Digital Twin Selector ===")
    for key, info in equipment.items():
        print(f"[{key}]-{info['name']}")

    selection = input("\nSelect the number of the equipment to control: ")

    if selection in equipment:
        config = equipment[selection]

        return config['class'](**config['params']), config['name']
    else:
        print("Selección no válida. Intente de nuevo.")
        return select_equipment()

def clear_console():
   os.system('cls' if os.name == 'nt' else 'clear')

def run_simulation():

    M1, equipament_name = select_equipment()

    try:
        instruction = float(input(f"Enter the target value for {equipament_name}: "))
    except ValueError:
        instruction = 1000.0
    
    update_interval = 1  
    

    print("-" * 50)
    print(f"Iniciando Gemelo Digital: {equipament_name}")
    print("-" * 50)

    try:
        while True:
            M1.PID(input_val=M1.sensor_value, Man_auto=False, SetpointAuto=instruction)
            M1.update(update_interval)
            
            clear_console()
        
            M1.display_status(instruction)
            print(f"\n-> Waiting {update_interval}s for next update...")

            controls = "[Controls] "
            if hasattr(M1, 'stop_sequence'):
                controls += "S: Safe Stop | "
            elif hasattr(M1, 'emergency_stop_trigger'):
              controls += "E: Emergency Stop | C: Change Setpoint | Ctrl+C: Exit"

            print(controls)

            time.sleep(update_interval)
          
            # 4. listen to commands (not blocking)
            if msvcrt.kbhit():
                keyboard_press = msvcrt.getch().decode().lower()
                if keyboard_press == 's' :
                    if hasattr(M1, 'stop_sequence'):
                        M1.stop_sequence()                     
                elif keyboard_press == 'e':
                    if hasattr(M1, 'emergency_stop_trigger'):
                        M1.emergency_stop_trigger()
                elif keyboard_press == 'c':
                        instruction = float(input("\nNew Target: "))

            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n\nEquipment control {equipament_name} finished.")
        retry = input("¿Want to control other equipment? (s/n): ")
        if retry.lower() == 's':
            run_simulation()

        # fn to save data on CSV

if __name__ == "__main__":
    run_simulation()