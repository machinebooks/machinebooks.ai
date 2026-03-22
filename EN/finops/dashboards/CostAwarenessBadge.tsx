// Source: The FinOps Engineer and the Machine -- Chapter 24
// Pattern: Cost awareness badge React component

// components/CostAwarenessBadge.tsx
// Shows the estimated cost of an operation before executing it.
// Integrates into any form that calls the LLM API.

import React, { useState, useEffect } from "react";

interface CostEstimate {
  modelo: string;
  input_tokens_est: number;
  coste_est_eur: number;
  alternativa?: {
    modelo: string;
    coste_est_eur: number;
    ahorro_pct: number;
  };
}

interface Props {
  prompt: string;
  systemPrompt?: string;
  modelo: string;
  operacionTipo: string;
  onAlternativaSeleccionada?: (modelo: string) => void;
}

export const CostAwarenessBadge: React.FC<Props> = ({
  prompt,
  systemPrompt = "",
  modelo,
  operacionTipo,
  onAlternativaSeleccionada,
}) => {
  const [estimate, setEstimate] = useState<CostEstimate | null>(null);

  useEffect(() => {
    // Estimate cost without making the actual call
    // Estimation is local: tokens approx. chars/4
    const inputTokensEst = Math.ceil(
      (prompt.length + systemPrompt.length) / 4
    );

    // Precios aproximados por modelo (EUR/token input)
    const precios: Record<string, number> = {
      "claude-opus-4-6": 0.000015,    // $15/1M tokens
      "claude-sonnet-4-6": 0.000003,  // $3/1M tokens
      "claude-haiku-4-5": 0.0000008, // $0.80/1M tokens
    };

    const precioModelo = precios[modelo] ?? 0.000003;
    const costeEst = inputTokensEst * precioModelo;

    // Is there a cheaper alternative?
    const tareasHaiku = ["clasificacion", "validacion", "extraccion", "routing"];
    let alternativa: CostEstimate["alternativa"] = undefined;

    if (
      tareasHaiku.some((t) => operacionTipo.toLowerCase().includes(t)) &&
      modelo !== "claude-haiku-4-5"
    ) {
      const costeHaiku = inputTokensEst * 0.0000008;
      alternativa = {
        modelo: "claude-haiku-4-5",
        coste_est_eur: costeHaiku,
        ahorro_pct: Math.round((1 - costeHaiku / costeEst) * 100),
      };
    }

    setEstimate({
      modelo,
      input_tokens_est: inputTokensEst,
      coste_est_eur: costeEst,
      alternativa,
    });
  }, [prompt, systemPrompt, modelo, operacionTipo]);

  if (!estimate) return null;

  const esCaro = estimate.coste_est_eur > 0.1; // Umbral visual

  return (
    <div className={`cost-badge ${esCaro ? "cost-badge--warning" : ""}`}>
      <span className="cost-badge__label">Estimated cost:</span>
      <span className="cost-badge__value">
        €{estimate.coste_est_eur.toFixed(4)}
      </span>
      <span className="cost-badge__tokens">
        (~{estimate.input_tokens_est.toLocaleString()} tokens)
      </span>

      {/* Cheaper alternative suggestion */}
      {estimate.alternativa && (
        <div className="cost-badge__alternativa">
          <span>
            {estimate.alternativa.modelo} would save{" "}
            {estimate.alternativa.ahorro_pct}%
          </span>
          {onAlternativaSeleccionada && (
            <button
              className="cost-badge__usar-alternativa"
              onClick={() =>
                onAlternativaSeleccionada(estimate.alternativa!.modelo)
              }
            >
              Usar {estimate.alternativa.modelo}
            </button>
          )}
        </div>
      )}
    </div>
  );
};
