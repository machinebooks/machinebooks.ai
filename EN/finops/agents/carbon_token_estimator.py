# Source: The FinOps Engineer and the Machine -- Chapter 29
# Pattern: Carbon footprint estimator for LLM usage

# services/carbon_token_estimator.py
# Estimates the energy footprint of LLM calls.
# IMPORTANT: estimated values, not measured. Do not use for formal reporting
# without provider validation.

from dataclasses import dataclass


@dataclass
class EmisionesLLM:
    """Estimated emission factors for an LLM model."""
    modelo: str
    kwh_por_1m_tokens_input: float
    kwh_por_1m_tokens_output: float
    pue_datacenter: float  # Datacenter PUE


class CarbonTokenEstimator:
    """
    Estimates the energy impact of LLM API calls.
    Based on Patterson et al. 2022 and Lottick et al. 2019.
    """

    FACTORES_EMISION = {
        "claude-haiku-4-5": EmisionesLLM("claude-haiku-4-5", 0.0005, 0.0020, 1.15),
        "claude-sonnet-4-6": EmisionesLLM("claude-sonnet-4-6", 0.0025, 0.0100, 1.15),
        "claude-opus-4-6": EmisionesLLM("claude-opus-4-6", 0.0120, 0.0480, 1.15),
    }

    # Emission factor by region (gCO2/kWh). Source: electricitymap.org 2024
    FACTORES_REGION = {
        "us-east-1": 395, "eu-west-1": 316, "eu-central-1": 401,
        "ap-southeast-1": 493, "us-west-2": 137,
    }

    def estimar_emisiones(
        self, modelo: str, input_tokens: int,
        output_tokens: int, region: str = "eu-west-1",
    ) -> dict:
        """Estimates energy consumption and CO2 emissions of an LLM call."""
        factores = self.FACTORES_EMISION.get(modelo)
        if not factores:
            return {"kwh": 0.0, "co2_gramos": 0.0, "disponible": False}

        factor_region = self.FACTORES_REGION.get(region, 400)
        kwh_input = input_tokens * factores.kwh_por_1m_tokens_input / 1_000_000
        kwh_output = output_tokens * factores.kwh_por_1m_tokens_output / 1_000_000
        kwh_total = (kwh_input + kwh_output) * factores.pue_datacenter
        co2_gramos = kwh_total * factor_region

        return {
            "kwh": round(kwh_total, 8),
            "co2_gramos": round(co2_gramos, 4),
            "region": region,
            "disponible": True,
            "nota": "Approximate estimate; do not use for formal reporting",
        }
