import React from 'react';
import { Activity, Server } from 'lucide-react';

export default function Header({ isConnected }) {
  return (
    <header className="flex items-center justify-between mb-8 border-b border-slate-700 pb-4">
      <div>
        <h1 className="text-3xl font-bold text-teal-400 tracking-tight flex items-center gap-3">
          <Activity className="w-8 h-8" />
          Digital Twin - HMI
        </h1>
        <p className="text-slate-400 mt-1 text-sm">Monitor de Equipamiento Industrial | React + FastAPI + BigQuery</p>
      </div>
      
      <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${isConnected ? 'bg-emerald-900/30 border-emerald-700' : 'bg-red-900/30 border-red-700'}`}>
        <Server className={`w-5 h-5 ${isConnected ? 'text-emerald-400' : 'text-red-400'}`} />
        <span className="font-mono text-sm">{isConnected ? 'API: CONECTADA' : 'API: OFFLINE'}</span>
      </div>
    </header>
  );
}