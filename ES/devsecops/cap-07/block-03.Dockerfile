# Extraído de: LibroDevSecOps/cap-07-contenedores.md
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
USER appuser
