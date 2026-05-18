import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TelemetryChart({ chartData }) {
  return (
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
  );
}