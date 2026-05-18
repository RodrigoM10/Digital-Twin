import React from 'react';
import { useSimulation } from './hooks/useSimulation';
import ControlPanel from './components/ControlPanel';
import ToastNotification from './components/ToastNotification';
import Header from './components/Header';
import TelemetryChart from './components/TelemtryChart';
import Indicators from './components/Indicators';



function App() {
  // Invocamos nuestro hook personalizado para traer toda la lógica
  const sim = useSimulation();

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans relative overflow-hidden">
      
      <ToastNotification message={sim.cloudMessage} />
      
      <Header isConnected={sim.isConnected} />

      <main className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Panel Izquierdo */}
        <ControlPanel 
          equipId={sim.equipId} 
          setEquipId={sim.setEquipId}
          target={sim.target} 
          setTarget={sim.setTarget}
          isRunning={sim.isRunning} 
          isStopping={sim.isStopping}
          onStart={sim.handleStart} 
          onStop={sim.handleStop} 
        />

        {/* Panel Central */}
        <div className="lg:col-span-3 space-y-6">
          <TelemetryChart chartData={sim.chartData} />
          
          <Indicators 
            telemetry={sim.telemetry} 
            target={sim.target} 
          />
        </div>
        
      </main>
    </div>
  );
}

export default App;