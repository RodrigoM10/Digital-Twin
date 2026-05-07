import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    from dashboard.app import app
except ImportError as e:
    print(f"Error al importar el Dashboard: {e}")
    print("Asegúrate de que la estructura sea: dashboard/app.py")
    sys.exit(1)

def start_system():
    clear_console = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear_console)

    print("="*50)
    print("   CENTRO DE CONTROL DIGITAL TWIN - ONLINE")
    print("="*50)
    print("\n[INFO] Iniciando servidor local...")
    print("[INFO] Accede a la interfaz en: http://127.0.0.1:8050/")
    print("[INFO] Presiona Ctrl+C para apagar el sistema.")
    print("-"*50)

    app.run(debug=True)

if __name__ == "__main__":
    start_system()