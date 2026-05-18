import React, { useState } from 'react';
import { useSimulation } from './hooks/useSimulation';
import { LayoutDashboard, Database } from 'lucide-react';
import ToastNotification from './components/ToastNotification';
import Header from './components/Header';
import ControlPanel from './components/ControlPanel';
import TelemetryChart from './components/TelemtryChart';
import Indicators from './components/Indicators';
import AnalyticsPanel from './components/AnalyticsPanel';

function App() {
  const sim = useSimulation();
  
  // AQUÍ ESTÁ LA VARIABLE QUE FALTABA: Define qué pestaña está activa
  const [activeTab, setActiveTab] = useState('monitor'); 

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans relative overflow-hidden">
      
      <ToastNotification message={sim.cloudMessage} />
      <Header isConnected={sim.isConnected} />

      {/* BARRA DE NAVEGACIÓN (TABS) */}
      <div className="flex gap-2 mb-6 border-b border-slate-700 pb-px">
        <button 
          onClick={() => setActiveTab('monitor')}
          className={`flex items-center gap-2 px-6 py-3 font-semibold rounded-t-lg transition-colors ${activeTab === 'monitor' ? 'bg-slate-800 text-teal-400 border-t-2 border-teal-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
        >
          <LayoutDashboard className="w-4 h-4" /> SCADA Monitor
        </button>
        <button 
          onClick={() => setActiveTab('analytics')}
          className={`flex items-center gap-2 px-6 py-3 font-semibold rounded-t-lg transition-colors ${activeTab === 'analytics' ? 'bg-slate-800 text-teal-400 border-t-2 border-teal-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
        >
          <Database className="w-4 h-4" /> Data Analytics
        </button>
      </div>

      {/* RENDERIZADO CONDICIONAL DE PESTAÑAS */}
      {activeTab === 'monitor' ? (
        <main className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <ControlPanel 
            equipId={sim.equipId} setEquipId={sim.setEquipId}
            target={sim.target} setTarget={sim.setTarget}
            isRunning={sim.isRunning} isStopping={sim.isStopping}
            onStart={sim.handleStart} onStop={sim.handleStop} 
          />
          <div className="lg:col-span-3 space-y-6">
            <TelemetryChart chartData={sim.chartData} />
            <Indicators telemetry={sim.telemetry} target={sim.target} />
          </div>
        </main>
      ) : (
        <AnalyticsPanel />
      )}
      
    </div>
  );
}

export default App;