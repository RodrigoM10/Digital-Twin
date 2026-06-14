"""
tuning · Toolkit modular de sintonización analítica de PID (FOPDT).

Paquete que separa, según principios SOLID, las responsabilidades antes mezcladas
en ``pid_sandbox.py``:

    core/           contratos abstractos (Plant, Controller, TuningRule)
    plants/         dinámica física de la planta
    controllers/    algoritmo de control (PID)
    simulation/     motor de experimentos (lazo abierto / cerrado)
    identification/ ajuste del modelo del proceso (FOPDT)
    tuning_rules/   reglas de ganancias (Ziegler-Nichols, Cohen-Coon)
    analysis/       métricas de desempeño
    reporting/      presentación de resultados

Punto de entrada: ``tune_engine.run()``.
"""
