# Extraído de: LibroTecnico/cap-16-react-ia.md
# frontend/app-analytics/Dockerfile
# Etapa 1: construcción
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

# Etapa 2: solo los assets estáticos
FROM alpine:latest AS dist
WORKDIR /dist
COPY --from=builder /app/dist .
