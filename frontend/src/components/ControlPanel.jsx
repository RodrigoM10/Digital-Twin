import React from 'react';
import { Play, Square, Loader2 } from 'lucide-react';

export default function ControlPanel({ 
  equipId, setEquipId, 
  target, setTarget, 
  isRunning, isStopping, 
  onStart, onStop 
}) {
  return (
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
            onClick={onStart}
            disabled={isRunning || isStopping}
            className="flex-1 bg-teal-600 hover:bg-teal-500 disabled:opacity-50 disabled:hover:bg-teal-600 text-white font-bold py-2 px-4 rounded flex justify-center items-center gap-2 transition-colors cursor-pointer disabled:cursor-not-allowed"
          >
            <Play className="w-4 h-4" /> START
          </button>
          
          <button 
            onClick={onStop}
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
  );
}