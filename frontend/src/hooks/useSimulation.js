import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const useSimulation = () => {
  const [equipId, setEquipId] = useState('1');
  const [target, setTarget] = useState(1000);
  const [isRunning, setIsRunning] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [cloudMessage, setCloudMessage] = useState('');
  const [chartData, setChartData] = useState([]);
  
  const [telemetry, setTelemetry] = useState({
    value: 0,
    valve: 0,
    status: { aux_motor: false, igniters: false, burners: false }
  });

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/sim/start/${equipId}`, { target: Number(target) });
      setIsRunning(true);
      setChartData([]); 
      setCloudMessage('');
    } catch (error) {
      console.error("Error iniciando:", error);
      alert("No se pudo conectar con el servidor Python.");
    }
  };

  const handleStop = () => {
    setIsStopping(true);
    setTimeout(() => {
      setIsRunning(false);
      setIsStopping(false);
      setCloudMessage('¡TELEMETRÍA COMPLETADA Y GUARDADA EN BIGQUERY! ☁️🎉');
      setTimeout(() => setCloudMessage(''), 5000);
    }, 1500);
  };

  useEffect(() => {
    let interval;
    const fetchTelemetry = async () => {
      try {
        const response = await axios.get(`${API_URL}/sim/telemetry`);
        setIsConnected(true);
        if (response.data.status !== "offline" && isRunning && !isStopping) {
          const newData = response.data;
          setTelemetry(newData);
          setChartData(prev => {
            const newPoint = { 
              time: new Date().toLocaleTimeString('es-AR', { hour12: false }), 
              Actual: newData.value, 
              Target: newData.target 
            };
            return [...prev.slice(-30), newPoint];
          });
        }
      } catch (error) {
        setIsConnected(false);
      }
    };

    if (isRunning && !isStopping) {
      interval = setInterval(fetchTelemetry, 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning, isStopping]);

  return {
    equipId, setEquipId,
    target, setTarget,
    isRunning, isConnected, isStopping,
    cloudMessage, telemetry, chartData,
    handleStart, handleStop
  };
};