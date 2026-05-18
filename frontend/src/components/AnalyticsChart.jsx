import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function AnalyticsChart({ results, activeQueryType }) {
  if (results.length === 0) return null;
  
  const chartData = results.map(row => ({
    ...row,
    timeLabel: row.timestamp ? new Date(row.timestamp).toLocaleTimeString('es-AR') : row.equipment
  }));

  const renderContent = () => {
    if (activeQueryType === 'recent') {
      return (
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="timeLabel" stroke="#94a3b8" tick={{fontSize: 12}} />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
          <Legend />
          <Line type="monotone" name="Valor Actual" dataKey="current_value" stroke="#2dd4bf" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="stepAfter" name="Target" dataKey="target" stroke="#f43f5e" strokeWidth={2} strokeDasharray="5 5" dot={false} />
        </LineChart>
      );
    }

    if (activeQueryType === 'stats') {
      return (
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="equipment" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
          <Legend />
          <Bar name="Promedio Histórico" dataKey="avg_value" fill="#34d399" radius={[4, 4, 0, 0]} />
          <Bar name="Apertura Max Válvula" dataKey="max_valve_aperture" fill="#60a5fa" radius={[4, 4, 0, 0]} />
        </BarChart>
      );
    }

    if (activeQueryType === 'overspeed') {
      return (
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="timeLabel" stroke="#94a3b8" tick={{fontSize: 12}} />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
          <Legend />
          <Line type="monotone" name="Desviación (RPM extra)" dataKey="deviation" stroke="#fbbf24" strokeWidth={3} dot={{ r: 4, fill: '#fbbf24' }} />
        </LineChart>
      );
    }
  };

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 h-72">
      <ResponsiveContainer width="100%" height="100%">
        {renderContent()}
      </ResponsiveContainer>
    </div>
  );
}