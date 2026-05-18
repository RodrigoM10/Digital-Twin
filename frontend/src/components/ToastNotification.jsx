import React from 'react';
import { CloudCheck } from 'lucide-react'; // Si da error, asegúrate de importar CloudCheck o usar CheckCircle

export default function ToastNotification({ message }) {
  if (!message) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 bg-teal-900/90 border-2 border-teal-400 text-teal-200 px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 animate-bounce backdrop-blur-sm">
      <CloudCheck className="w-6 h-6 text-teal-400 animate-pulse" />
      <span className="font-semibold text-sm tracking-wide">{message}</span>
    </div>
  );
}