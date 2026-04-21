import time
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importamos el gemelo digital específico
# Nota: Si cambias de equipo, solo cambias esta importación
from models.pump_system import ControlledPump

def run_simulation():
    # --- CONFIGURACIÓN ---
    update_interval = 1  
    instruction = 1500  
    
    M1 = ControlledPump(MaxRPM=4000, kP=10.0, kI=0.0001, kD=0.01)

    print("-" * 50)
    print(f"Iniciando Gemelo Digital: {M1.__class__.__name__}")
    print(f"Objetivo: {instruction} unidades")
    print("-" * 50)

    try:
        while True:
            # 1. El cerebro (PID) calcula cuánto abrir la válvula
            M1.PID(input_val=M1.RPM, Man_auto=False, SetpointAuto=instruction)
            
            # 2. La física (Bomba) se actualiza según la posición de la válvula
            M1.update(update_interval)
            
            # 3. Visualización de datos en tiempo real
            output = (
                f"instruction: {instruction} | "
                f"Real Speed: {M1.RPM:>8.2f} | "
                f"Valve: {M1.Valve:>6.2f}%"
            )
            print(output, end="\r")
            
            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("\n\nSimulación finalizada por el usuario.")

        # añadir una función para guardar los datos en un CSV

if __name__ == "__main__":
    run_simulation()