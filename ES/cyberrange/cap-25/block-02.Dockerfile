# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/docker/frontend-multistage.Dockerfile

# Stage 1: Build — Node 20 con todas las dependencias de desarrollo
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci                              # Instalación determinista desde lockfile
COPY . .
ARG VITE_API_BASE_URL=                  # Vacío = URLs relativas (funciona desde cualquier host)
ARG VITE_API_PROTOCOL=
RUN npx vite build                      # Genera /app/dist con los assets optimizados

# Stage 2: Serve — Nginx Alpine (15 MB) sirve los archivos estáticos
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
