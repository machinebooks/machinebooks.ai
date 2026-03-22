// Source: The FinOps Engineer and the Machine -- Chapter 29
// Pattern: Sustainability dashboard React component

// components/SustainabilityDashboard.tsx
// Unified dashboard: economic, energy and carbon cost.

import React, { useState, useEffect } from "react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis,
         CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface MetricaUnificada {
  periodo: string;
  coste_tokens_eur: number;
  coste_cloud_eur: number;
  coste_personas_eur: number;
  coste_total_eur: number;
  kwh_total: number;
  co2_kg_total: number;
  roi: number;
}

export const SustainabilityDashboard: React.FC<{
  proyecto_codigo: string; meses: number;
}> = ({ proyecto_codigo, meses = 6 }) => {
  const [metricas, setMetricas] = useState<MetricaUnificada[]>([]);
  const [vista, setVista] = useState<"economica" | "energia" | "carbono">(
    "economica"
  );

  useEffect(() => {
    fetch(`/api/finops/sostenibilidad/${proyecto_codigo}?meses=${meses}`)
      .then(r => r.json())
      .then(d => setMetricas(d.metricas));
  }, [proyecto_codigo, meses]);

  const ultimo = metricas[metricas.length - 1];

  return (
    <div className="p-6">
      {/* View selector: economic, energy or carbon */}
      <div className="flex gap-2 mb-6">
        {(["economica", "energia", "carbono"] as const).map(v => (
          <button key={v} onClick={() => setVista(v)}
            className={vista === v ? "bg-blue-600 text-white px-4 py-2 rounded"
              : "bg-gray-100 px-4 py-2 rounded"}>
            {v.charAt(0).toUpperCase() + v.slice(1)}
          </button>
        ))}
      </div>

      {/* KPIs for the latest period */}
      {ultimo && (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-4 rounded shadow-sm">
            <div className="text-sm text-gray-500">Coste total</div>
            <div className="text-2xl font-bold">
              €{ultimo.coste_total_eur.toLocaleString("es-ES")}
            </div>
          </div>
          <div className="bg-white p-4 rounded shadow-sm">
            <div className="text-sm text-gray-500">Energy</div>
            <div className="text-2xl font-bold text-blue-600">
              {ultimo.kwh_total.toFixed(1)} kWh
            </div>
          </div>
          <div className="bg-white p-4 rounded shadow-sm">
            <div className="text-sm text-gray-500">CO₂</div>
            <div className="text-2xl font-bold text-green-600">
              {ultimo.co2_kg_total < 1
                ? `${(ultimo.co2_kg_total * 1000).toFixed(0)}g`
                : `${ultimo.co2_kg_total.toFixed(2)}kg`}
            </div>
          </div>
          <div className="bg-white p-4 rounded shadow-sm">
            <div className="text-sm text-gray-500">ROI</div>
            <div className="text-2xl font-bold text-purple-600">
              {ultimo.roi.toFixed(1)}×
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
