import pandas as pd
import matplotlib.pyplot as plt

def analyze_results(filename):
    try:
        data = pd.read_csv(filename)
        
        if data.empty:
            print("No hay datos para analizar.")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        fig.suptitle(f'Digital Twin Performance Analysis: {data["Equipment"].iloc[0]}')

        # Figure 1: Real value vs Target
        ax1.plot(data.index, data['Current_Value'], label='Actual Value', color='blue', linewidth=2)
        ax1.plot(data.index, data['Target'], label='Target', color='red', linestyle='--', alpha=0.8)
        ax1.set_ylabel('Process Variable')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # Figure 2: PID OutputEsfuerzo de la Válvula (PID Output)
        ax2.fill_between(data.index, data['Valve_Pos'], color='green', alpha=0.2)
        ax2.plot(data.index, data['Valve_Pos'], label='Valve Position (%)', color='green')
        ax2.set_ylabel('Valve %')
        ax2.set_xlabel('Sample Points')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        print(f"\n[ANALYSIS] Generating charts for {filename}...")
        plt.show()

    except Exception as e:
        print(f"Error durante el análisis: {e}")