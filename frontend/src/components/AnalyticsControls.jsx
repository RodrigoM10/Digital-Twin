import React from 'react';
import { Database, Search, AlertCircle, BarChart2 } from 'lucide-react';

export default function AnalyticsControls({ 
  equipName, setEquipName, 
  fetchQuery, loading, activeQueryType 
}) {
  return (
    <>
      <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center mb-6 border-b border-slate-700 pb-6">
        <div>
          <h2 className="text-2xl font-bold text-teal-400 flex items-center gap-2">
            <Database className="w-6 h-6" />
            BigQuery Analytics
          </h2>
          <p className="text-slate-400 text-sm mt-1">Análisis visual y tabular de registros históricos (50 registros máximos)</p>
        </div>

        <select 
          value={equipName} 
          onChange={(e) => setEquipName(e.target.value)}
          className="bg-slate-900 border border-slate-600 rounded p-2 text-slate-200 focus:outline-none focus:border-teal-400 w-full md:w-auto font-semibold"
        >
          <option value="Pump (RPM)">Pump (RPM)</option>
          <option value="Water Tank (Level %)">Water Tank (Level %)</option>
          <option value="Gas Turbine (RPM)">Gas Turbine (RPM)</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <button onClick={() => fetchQuery('recent')} disabled={loading} className={`py-3 px-4 rounded-lg flex flex-col items-center gap-2 border transition-colors ${activeQueryType === 'recent' ? 'bg-slate-700 border-teal-400 shadow-[0_0_15px_rgba(45,212,191,0.2)]' : 'bg-slate-800 border-slate-600 hover:bg-slate-700'}`}>
          <Search className="w-5 h-5 text-blue-400" /> Historial Reciente
        </button>
        <button onClick={() => fetchQuery('stats')} disabled={loading} className={`py-3 px-4 rounded-lg flex flex-col items-center gap-2 border transition-colors ${activeQueryType === 'stats' ? 'bg-slate-700 border-teal-400 shadow-[0_0_15px_rgba(45,212,191,0.2)]' : 'bg-slate-800 border-slate-600 hover:bg-slate-700'}`}>
          <BarChart2 className="w-5 h-5 text-emerald-400" /> Estadísticas Globales
        </button>
        <button onClick={() => fetchQuery('overspeed')} disabled={loading} className={`py-3 px-4 rounded-lg flex flex-col items-center gap-2 border transition-colors ${activeQueryType === 'overspeed' ? 'bg-slate-700 border-teal-400 shadow-[0_0_15px_rgba(45,212,191,0.2)]' : 'bg-slate-800 border-slate-600 hover:bg-slate-700'}`}>
          <AlertCircle className="w-5 h-5 text-rose-400" /> Alertas de Desviación
        </button>
      </div>
    </>
  );
}