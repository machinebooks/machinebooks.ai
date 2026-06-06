# Extracted from: LibroAIGateway/cap-24-telemetry-realtime-webhooks.md
# metrics_service.py: histogram definition
n7x_request_duration_seconds = Histogram(
    "n7x_request_duration_seconds",
    "Request latency in seconds",
    labelnames=["endpoint", "model"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)
