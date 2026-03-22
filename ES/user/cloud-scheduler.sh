# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
#!/bin/bash
# cloud-scheduler.sh — Encender/apagar instancias dev
# Uso: ./cloud-scheduler.sh start|stop

ACTION=$1
ENV_FILTER="Name=tag:Environment,Values=development"

if [ "$ACTION" = "stop" ]; then
    echo "Apagando instancias de desarrollo..."
    INSTANCES=$(aws ec2 describe-instances \
        --filters "$ENV_FILTER" "Name=instance-state-name,Values=running" \
        --query 'Reservations[].Instances[].InstanceId' \
        --output text)
    if [ ! -z "$INSTANCES" ]; then
        aws ec2 stop-instances --instance-ids $INSTANCES
        echo "Apagadas: $INSTANCES"
    else
        echo "No hay instancias de desarrollo corriendo."
    fi

elif [ "$ACTION" = "start" ]; then
    echo "Encendiendo instancias de desarrollo..."
    INSTANCES=$(aws ec2 describe-instances \
        --filters "$ENV_FILTER" "Name=instance-state-name,Values=stopped" \
        --query 'Reservations[].Instances[].InstanceId' \
        --output text)
    if [ ! -z "$INSTANCES" ]; then
        aws ec2 start-instances --instance-ids $INSTANCES
        echo "Encendidas: $INSTANCES"
    else
        echo "No hay instancias de desarrollo paradas."
    fi
fi
