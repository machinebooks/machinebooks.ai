# Extraído de: LibroAIGateway/cap-24-telemetria-realtime-webhooks.md
# metrics_service.py: definición del histograma
n7x_request_duration_seconds = Histogram(
    "n7x_request_duration_seconds",
    "Latencia del request en segundos",
    labelnames=["endpoint", "model"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)
