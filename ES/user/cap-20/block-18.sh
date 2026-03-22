# Extraído de: LibroUsuario/cap-20-servidores-y-servicios.md
# Crear override de systemd para limitar memoria
sudo mkdir -p /etc/systemd/system/webapp.service.d/
cat <<EOF | sudo tee /etc/systemd/system/webapp.service.d/memory-limit.conf
[Service]
MemoryMax=2G
MemoryHigh=1.5G
Restart=on-failure
RestartSec=10
EOF

sudo systemctl daemon-reload
sudo systemctl restart webapp
