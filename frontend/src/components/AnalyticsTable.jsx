import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function AnalyticsTable({ results }) {
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 10;

  // Reiniciar la página si cambian los resultados
  useEffect(() => {
    setCurrentPage(1);
  }, [results]);

  const totalPages = Math.ceil(results.length / ITEMS_PER_PAGE);
  const paginatedData = results.slice(
    (currentPage - 1) * ITEMS_PER_PAGE, 
    currentPage * ITEMS_PER_PAGE
  );

  if (results.length === 0) return null;

  return (
    <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300 mb-4">
          <thead className="text-xs uppercase bg-slate-800 text-slate-400">
            <tr>
              {Object.keys(paginatedData[0]).map((key) => (
                <th key={key} className="px-4 py-3">{key.replace('_', ' ')}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, idx) => (
              <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800 transition-colors">
                {Object.values(row).map((val, i) => (
                  <td key={i} className="px-4 py-3 font-mono">{String(val)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-700 pt-4 mt-2">
          <span className="text-sm text-slate-400">
            Mostrando {(currentPage - 1) * ITEMS_PER_PAGE + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, results.length)} de {results.length} registros
          </span>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-50 disabled:hover:bg-slate-800 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="px-4 py-2 bg-slate-800 rounded font-mono text-sm text-teal-400 border border-slate-700">
              {currentPage} / {totalPages}
            </div>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-50 disabled:hover:bg-slate-800 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}