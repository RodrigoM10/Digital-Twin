# 🏭 Digital Twin & Cloud SCADA HMI

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF.svg)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-BigQuery-4285F4.svg)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC.svg)

## 📌 Descripción del Proyecto
Este proyecto es una implementación completa **End-to-End** de un Gemelo Digital (Digital Twin) para equipamiento industrial. Fusiona la ingeniería de procesos con el Data Engineering moderno, simulando el comportamiento físico y el control automático (PID) de sistemas reales, mientras transmite telemetría asíncrona a la nube para su monitoreo y análisis en una interfaz web de alto rendimiento.

**El objetivo:** Demostrar una arquitectura desacoplada y escalable, donde un motor físico en Python alimenta una SPA (Single Page Application) en React, gestionando el flujo de datos históricos hacia un Data Warehouse cloud-native.

---

## 📸 Demostración en vercel: 
https://digital-twin-wine.vercel.app/

---

## 🚀 Características Principales

* **Arquitectura Desacoplada (API REST):** El "cerebro" (FastAPI) y la "vista" (React) operan de forma independiente, comunicándose vía HTTP/Axios para una escalabilidad óptima.
* **Simulación Física y Control PID:** Modelado matemático de equipos industriales (Bombas, Tanques, Turbinas) operando con lazos de control cerrados y resolución de 1 segundo.
* **Ingesta Asíncrona en la Nube (Background Tasks):** Integración nativa con **Google BigQuery**. Los datos de telemetría se envían a la nube en segundo plano (Streaming Inserts) sin bloquear la respuesta de la API ni frenar el ciclo de la simulación.
* **HMI Reactivo y de Alto Rendimiento:** Frontend desarrollado con React y Vite. Gráficos en tiempo real (Recharts) que plotean la dinámica de proceso frente al *setpoint* de manera fluida y sin recargas de página.
* **Data Analytics & Business Intelligence:** Pestaña analítica dedicada que ejecuta consultas SQL parametrizadas (seguras contra inyecciones) en BigQuery, mostrando estadísticas, tablas paginadas y permitiendo la exportación de reportes a **CSV** para los *stakeholders* del negocio.

---

## 🏗️ Estructura del Monorepo

El proyecto está organizado en un único repositorio con responsabilidades claramente separadas:

```text
Digital-Twin/
├── backend/                  # Cerebro y Física (Python)
│   ├── models/               # Clases de simulación (Controladores PID)
│   ├── server.py             # Rutas FastAPI y lógica de BigQuery
│   ├── main.py               # Lanzador Uvicorn
│   └── requirements.txt      # Dependencias (FastAPI, Google Cloud, etc.)
│
└── frontend/                 # Interfaz de Usuario (Node.js)
    ├── src/
    │   ├── components/       # Componentes modulares (Gráficos, Tablas, Controles)
    │   ├── hooks/            # Custom hooks para lógica y estados (useSimulation)
    │   └── App.jsx           # Orquestador principal
    ├── package.json
    └── vite.config.js
```

## ⚙️ Instalación y Uso

### 1. Clonar el repositorio

```bash
<<<<<<< HEAD
git clone [https://github.com/TU_USUARIO/Digital-Twin.git](https://github.com/TU_USUARIO/Digital-Twin.git)
cd Digital-Twin
```
### 2. Configurar el Backend (Python / FastAPI)
```bash
cd backend
python -m venv .venv

# Activar entorno (Windows):
.\.venv\Scripts\activate
# Activar entorno (Mac/Linux):
source .venv/bin/activate

# Instalar dependencias exactas
pip install fastapi==0.104.1 pydantic==2.5.3 uvicorn google-cloud-bigquery cryptography==41.0.7
```

Credenciales GCP: Descarga tu clave de cuenta de servicio de Google Cloud (con permisos de inserción y lectura en BigQuery), renómbrala a gcp_credentials.json y colócala en la carpeta backend/.

Ejecutar Servidor API:
```bash
python main.py
# El servidor correrá en [http://127.0.0.1:8000](http://127.0.0.1:8000)
```
### 3. Configurar el Frontend (React / Vite)

```bash
cd frontend

# Instalar paquetes de Node
npm install

# Iniciar entorno de desarrollo ultra-rápido
npm run dev
# La aplicación abrirá en http://localhost:5173/
```

### 4. Variables de Entorno (Opcional - Para Producción)
Si deseas desplegar el frontend (ej. Vercel) apuntando a un backend alojado en la nube, crea un archivo .env en la carpeta frontend/:

VITE_API_URL=[https://tu-api-en-produccion.com](https://tu-api-en-produccion.com)


Desarrollado con enfoque en automatización, datos enfocados al negocio y arquitectura de software moderna.
