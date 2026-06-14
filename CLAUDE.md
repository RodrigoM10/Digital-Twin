# Instrucciones del Proyecto: Digital Twin SCADA

## Comandos Personalizados
Si el usuario escribe un comando que empieza con `/`, busca su definición aquí y ejecuta las instrucciones asociadas paso a paso.

### Comando: `/tune-pid`
**Objetivo:** Predecir analíticamente las constantes óptimas del controlador PID (`Kp`, `Ki`, `Kd`) para un equipo, mediante identificación del proceso, sin recurrir a prueba y error.

**Herramienta:** `backend/models/tuning/` — paquete modular (refactor SOLID del antiguo `pid_sandbox.py`) cuyo punto de entrada es `backend/models/tuning/tune_engine.py`. Implementa el flujo completo:
1. **Respuesta al escalón en lazo abierto** (Open-Loop Step Response) sobre un modelo de planta auto-regulado.
2. **Identificación FOPDT** por el método de dos puntos de Smith (28.3% / 63.2%): obtiene la ganancia estática `K`, la constante de tiempo `τ` y el tiempo muerto `L`.
3. **Predicción de ganancias** con reglas analíticas de **Ziegler-Nichols** (curva de reacción) y **Cohen-Coon**.
4. **Validación en lazo cerrado** con un PID posicional estándar (incluye anti-windup): reporta Overshoot y Settling Time.

**Ecuación de control de referencia:** $$u(t) = K_p e(t) + K_i \int_{0}^{t} e(\tau) d\tau + K_d \frac{de(t)}{dt}$$

**Instrucciones para Claude:**
1. Lee `backend/models/tuning/tune_engine.py` para entender el flujo y los parámetros editables (`STEP_U0`, `STEP_U1`, `SETPOINT`, `MANUAL_GAINS`). El modelo de planta vive en `tuning/plants/pump_plant.py` (`PumpPlant`).
2. Si el usuario pide afinar un punto de operación concreto, ajusta esos parámetros (o el modelo `PumpPlant`) según tu análisis del sistema.
3. Ejecuta el motor con `python backend/models/tuning/tune_engine.py`.
4. Analiza la salida: parámetros FOPDT identificados, ganancias predichas (ZN vs Cohen-Coon) y métricas de lazo cerrado (Overshoot, Settling Time, error permanente).
5. Para evaluar ganancias propuestas por el usuario, cárgalas en `MANUAL_GAINS` y vuelve a ejecutar para comparar. Para agregar una nueva regla de sintonización, crea un archivo en `tuning/tuning_rules/` (subclase de `TuningRule`) y añádela a la lista de reglas en `tune_engine.run()`.
6. Sugiere al usuario los valores óptimos y, **antes de proponer aplicarlos al modelo de producción**, recuérdale las advertencias que imprime el motor: el PID de producción (`backend/models/pid_controller.py`) es de **forma incremental** (no posicional), por lo que las ganancias son un punto de partida y deben revalidarse en el lazo real.
