# Extraído de: LibroTecnico/cap-11-integracion-llms.md
import asyncio

# Máximo de llamadas LLM concurrentes (límite del proveedor)
LLM_SEMAPHORE = asyncio.Semaphore(5)

# Máximo de análisis de documentos concurrentes (~11 llamadas LLM cada uno)
DOCUMENT_ANALYSIS_SEMAPHORE = asyncio.Semaphore(3)

# Máximo de evaluaciones concurrentes (~8 llamadas LLM cada una)
EVALUATION_SEMAPHORE = asyncio.Semaphore(3)

# Máximo de lecturas de documentos concurrentes
DOCUMENT_READ_SEMAPHORE = asyncio.Semaphore(10)
