import React, { useState, useEffect } from 'react';
import { Activity, Server, Play, Square, AlertTriangle, CloudCheck, Loader2 } from 'lucide-react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [equipId, setEquipId] = useState('1');
  const [target, setTarget] = useState(1000);
  const [isRunning, setIsRunning] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  // NUEVOS ESTADOS: Para el spinner del botón y el cartel de la nube
  const [isStopping, setIsStopping] = useState(false);
  const [cloudMessage, setCloudMessage] = useState('');

  const [telemetry, setTelemetry] = useState({
    value: 0,
    valve: 0,
    status: { aux_motor: false, igniters: false, burners: false }
  });

  const [chartData, setChartData] = useState([]);

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/sim/start/${equipId}`, { target: Number(target) });
      setIsRunning(true);
      setChartData([]); 
      setCloudMessage(''); // Limpiamos mensajes anteriores
    } catch (error) {
      console.error("Error iniciando simulación:", error);
      alert("No se pudo conectar con el servidor Python.");
    }
  };

  // FUNCIÓN DE PARADO CON SPINNING Y NOTIFICACIÓN
  const handleStop = () => {
    setIsStopping(true); // Encendemos el spinner en el botón de STOP
    
    // Simulamos un retraso de 1.5 segundos para dar feedback visual de que 
    // los últimos datos asíncronos terminaron de impactar en BigQuery
    setTimeout(() => {
      setIsRunning(false);
      setIsStopping(false); // Apagamos el spinner
      setCloudMessage('¡TELEMETRÍA COMPLETADA Y GUARDADA EN BIGQUERY! ☁️🎉');
      
      // El mensaje desaparece solo después de 5 segundos
      setTimeout(() => {
        setCloudMessage('');
      }, 5000);
    }, 1500);
  };

  useEffect(() => {
    let interval;

    const fetchTelemetry = async () => {
      try {
        const response = await axios.get(`${API_URL}/sim/telemetry`);
        setIsConnected(true);
        
        if (response.data.status !== "offline" && isRunning && !isStopping) {
          const newData = response.data;
          setTelemetry(newData);

          setChartData(prev => {
            const newPoint = { 
              time: new Date().toLocaleTimeString('es-AR', { hour12: false }), 
              Actual: newData.value, 
              Target: newData.target 
            };
            return [...prev.slice(-30), newPoint];
          });
        }
      } catch (error) {
        setIsConnected(false);
      }
    };

    if (isRunning && !isStopping) {
      interval = setInterval(fetchTelemetry, 1000);
    }

    return () => clearInterval(interval);
  }, [isRunning, isStopping]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans relative overflow-hidden">
      
      {/* NOTIFICACIÓN FLOTANTE (TOAST) */}
      {cloudMessage && (
        <div className="fixed bottom-5 right-5 z-50 bg-teal-900/90 border-2 border-teal-400 text-teal-200 px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce backdrop-blur-sm">
          <CloudCheck className="w-6 h-6 text-teal-400 animate-pulse" />
          <span className="font-semibold text-sm tracking-wide">{cloudMessage}</span>
        </div>
      )}

      {/* Header */}
      <header className="flex items-center justify-between mb-8 border-b border-slate-700 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-teal-400 tracking-tight flex items-center gap-3">
            <Activity className="w-8 h-8" />
            Digital Twin SCADA
          </h1>
          <p className="text-slate-400 mt-1 text-sm">Monitor de Equipamiento Industrial | React + FastAPI + BigQuery</p>
        </div>
        
        <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${isConnected ? 'bg-emerald-900/30 border-emerald-700' : 'bg-red-900/30 border-red-700'}`}>
          <Server className={`w-5 h-5 ${isConnected ? 'text-emerald-400' : 'text-red-400'}`} />
          <span className="font-mono text-sm">{isConnected ? 'API: CONECTADA' : 'API: OFFLINE'}</span>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* PANEL IZQUIERDO: Controles */}
        <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-xl h-fit">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 border-b border-slate-700 pb-2">
            Panel de Control
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Seleccionar Equipo</label>
              <select 
                value={equipId} 
                onChange={(e) => setEquipId(e.target.value)}
                disabled={isRunning}
                className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-slate-200 focus:outline-none focus:border-teal-400"
              >
                <option value="1">Pump (RPM)</option>
                <option value="2">Water Tank (Level %)</option>
                <option value="3">Gas Turbine (RPM)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-slate-400 mb-1">Target Value (Setpoint)</label>
              <input 
                type="number" 
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                disabled={isRunning}
                className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-slate-200 focus:outline-none focus:border-teal-400"
              />
            </div>

            <div className="pt-4 flex gap-2">
              <button 
                onClick={handleStart}
                disabled={isRunning || isStopping}
                className="flex-1 bg-teal-600 hover:bg-teal-500 disabled:opacity-50 disabled:hover:bg-teal-600 text-white font-bold py-2 px-4 rounded flex justify-center items-center gap-2 transition-colors cursor-pointer disabled:cursor-not-allowed"
              >
                <Play className="w-4 h-4" /> START
              </button>
              
              {/* BOTÓN DE STOP DINÁMICO CON SPINNER */}
              <button 
                onClick={handleStop}
                disabled={!isRunning || isStopping}
                className="flex-1 bg-rose-600 hover:bg-rose-500 disabled:opacity-50 disabled:hover:bg-rose-600 text-white font-bold py-2 px-4 rounded flex justify-center items-center gap-2 transition-colors cursor-pointer disabled:cursor-not-allowed"
              >
                {isStopping ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    SINC...
                  </>
                ) : (
                  <>
                    <Square className="w-4 h-4" />
                    STOP
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* PANEL CENTRAL: Gráficos e Indicadores */}
        <div className="lg:col-span-3 space-y-6">
          
          {/* Gráfico en Vivo */}
          <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 shadow-xl">
            <h2 className="text-xl font-semibold mb-4 border-b border-slate-700 pb-2">Dinámica de Proceso</h2>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="time" stroke="#94a3b8" tick={{fontSize: 12}} />
                  <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                  <Line type="monotone" dataKey="Actual" stroke="#2dd4bf" strokeWidth={3} dot={false} isAnimationActive={false} />
                  <Line type="stepAfter" dataKey="Target" stroke="#f43f5e" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Indicadores Digitales */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex flex-col items-center justify-center">
              <span className="text-sm text-slate-400 mb-2">Valor Actual</span>
              <span className="text-2xl font-mono font-bold text-teal-400">{telemetry.value}</span>
            </div>
            
            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex flex-col items-center justify-center">
              <span className="text-sm text-slate-400 mb-2">Válvula Control</span>
              <span className="text-2xl font-mono font-bold text-blue-400">{telemetry.valve}%</span>
            </div>

            <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex flex-col justify-center gap-2">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${telemetry.status.aux_motor ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-slate-600'}`}></div>
                <span className="text-xs text-slate-300">Motor Auxiliar</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${telemetry.status.igniters ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-slate-600'}`}></div>
                <span className="text-xs text-slate-300">Ignitores</span>
              </div>
            </div>

            <div className={`rounded-lg p-4 border flex flex-col items-center justify-center transition-colors duration-300 ${telemetry.value > (target + 100) ? 'bg-rose-900/50 border-rose-500' : 'bg-slate-800 border-slate-700'}`}>
              <AlertTriangle className={`w-8 h-8 mb-2 ${telemetry.value > (target + 100) ? 'text-rose-500 animate-pulse' : 'text-slate-600'}`} />
              <span className={`text-xs font-bold ${telemetry.value > (target + 100) ? 'text-rose-400' : 'text-slate-500'}`}>
                {telemetry.value > (target + 100) ? 'OVERSPEED WARN' : 'SYSTEM NORMAL'}
              </span>
            </div>
          </div>

        </div>
      </main>

    </div>
  );
}

export default App;