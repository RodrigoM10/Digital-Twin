import React, { useState } from 'react';
import axios from 'axios';
import { Database, Loader2 } from 'lucide-react';

import AnalyticsControls from './AnalyticsControls';
import AnalyticsChart from './AnalyticsChart';
import AnalyticsTable from './AnalyticsTable';

const API_URL = 'http://127.0.0.1:8000';

export default function AnalyticsPanel() {
  const [equipName, setEquipName] = useState('Pump (RPM)');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [activeQueryType, setActiveQueryType] = useState(null);

  const fetchQuery = async (queryId) => {
    setLoading(true);
    setResults([]);
    setActiveQueryType(queryId);

    try {
      const response = await axios.get(`${API_URL}/sim/analytics/${queryId}`, {
        params: { equip_name: equipName }
      });
      setResults(response.data.data);
    } catch (error) {
      console.error("Error trayendo datos:", error);
      alert("Hubo un error al consultar BigQuery.");
    }
    setLoading(false);
  };

  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-xl min-h-[500px] flex flex-col">
      
      {/* Componente 1: Controles Superiores */}
      <AnalyticsControls 
        equipName={equipName}
        setEquipName={setEquipName}
        fetchQuery={fetchQuery}
        loading={loading}
        activeQueryType={activeQueryType}
      />

      {/* Área Central: Estados de Carga o Resultados */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400 flex-grow">
          <Loader2 className="w-10 h-10 animate-spin mb-4 text-teal-500" />
          <span className="font-mono text-sm animate-pulse">Ejecutando consulta en BigQuery...</span>
        </div>
      ) : results.length > 0 ? (
        <div className="flex flex-col gap-6 flex-grow">
          {/* Componente 2: Gráfico Dinámico */}
          <AnalyticsChart results={results} activeQueryType={activeQueryType} />
          
          {/* Componente 3: Tabla Paginada */}
          <AnalyticsTable results={results} />
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500 flex-grow border-2 border-dashed border-slate-700 rounded-lg">
          <Database className="w-12 h-12 mb-3 text-slate-600 opacity-50" />
          <p>Seleccioná una consulta arriba para visualizar los datos históricos.</p>
        </div>
      )}

    </div>
  );
}