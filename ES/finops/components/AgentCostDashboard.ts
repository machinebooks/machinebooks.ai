// Extraído de: LibroFinOps/cap-28-finops-agentes-autonomos.md
// components/AgentCostDashboard.tsx
// Dashboard para monitorizar el coste de agentes en tiempo real.

import React, { useState, useEffect } from "react";

interface AgentSession {
  session_id: string;
  agente_tipo: string;
  objetivo: string;
  presupuesto_eur: number | null;
  total_cost_eur: number;
  pct_presupuesto: number;
  num_llamadas: number;
  estado: "activa" | "completada" | "detenida_por_presupuesto";
  duracion_minutos: number;
}

export const AgentCostDashboard: React.FC = () => {
  const [sesiones, setSesiones] = useState<AgentSession[]>([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch("/api/finops/agentes/sesiones-activas");
      const data = await response.json();
      setSesiones(data.sesiones);
    }, 30_000); // Refresco cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  const colorEstado = (s: AgentSession) => {
    if (s.estado === "detenida_por_presupuesto") return "text-red-600";
    if (s.pct_presupuesto > 85) return "text-yellow-600";
    return "text-green-600";
  };

  return (
    <div className="agent-dashboard p-4">
      <h2 className="text-xl font-bold mb-4">
        Agentes Autónomos — Coste en Tiempo Real
      </h2>
      {sesiones.map((s) => (
        <div key={s.session_id} className="border rounded-lg p-4 mb-3">
          <div className="flex justify-between">
            <span className="font-mono text-sm text-gray-500">
              {s.agente_tipo}
            </span>
            <span className={`font-bold ${colorEstado(s)}`}>
              €{s.total_cost_eur.toFixed(4)}
            </span>
          </div>
          <p className="text-sm truncate my-1">{s.objetivo}</p>

          {s.presupuesto_eur && (
            <div>
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>{s.pct_presupuesto.toFixed(1)}% usado</span>
                <span>de €{s.presupuesto_eur.toFixed(4)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    s.pct_presupuesto > 90 ? "bg-red-500" :
                    s.pct_presupuesto > 70 ? "bg-yellow-500" : "bg-green-500"
                  }`}
                  style={{ width: `${Math.min(s.pct_presupuesto, 100)}%` }}
                />
              </div>
            </div>
          )}

          <div className="mt-2 flex gap-4 text-xs text-gray-500">
            <span>{s.num_llamadas} llamadas LLM</span>
            <span>{s.duracion_minutos.toFixed(1)} min</span>
            <span className={`font-medium ${colorEstado(s)}`}>
              {s.estado}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
