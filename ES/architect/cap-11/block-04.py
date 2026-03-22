# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# En create_native_client() de la factoría
client, model = _create_native_from_config(config)
# Envolver con tracker antes de devolver
tracked = NativeClientUsageTracker(client, model, service_type, config['provider_type'])
return tracked, model
