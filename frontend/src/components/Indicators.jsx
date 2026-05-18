import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function Indicators({ telemetry, target }) {
  return (
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
  );
}