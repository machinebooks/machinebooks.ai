# Extraído de: LibroCyberrange/cap-04-claude-ecosistema.md
# Servidor MCP para operaciones de Proxmox
# Ejemplo didáctico: patrones/mcp/proxmox_server.py

from mcp.server import Server
from mcp.types import TextContent
import json

server = Server("proxmox-operations")

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """Gestiona las llamadas a herramientas de Proxmox.

    Cada herramienta opera con credenciales de mínimo privilegio:
    el servidor MCP tiene un token de Proxmox con permisos limitados
    a las operaciones que el agente necesita.
    """
    if name == "list_templates":
        # Listar templates disponibles para clonación
        templates = await proxmox_client.get_templates(
            node=arguments.get("node", "pve-node-01")
        )
        return [TextContent(
            type="text",
            text=json.dumps(templates, indent=2)
        )]

    elif name == "clone_vm":
        # Clonar una VM desde template — con validación
        template_id = arguments["template_id"]
        target_name = arguments["target_name"]
        workzone_id = arguments["workzone_id"]

        # Verificar que el template existe y es clonable
        if not await proxmox_client.template_exists(template_id):
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Template {template_id} no existe"})
            )]

        # Verificar recursos disponibles antes de clonar
        resources = await proxmox_client.check_resources()
        if resources["free_ram_gb"] < 4:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Recursos insuficientes",
                    "free_ram_gb": resources["free_ram_gb"],
                    "suggestion": "Usar template con menor consumo de RAM"
                })
            )]

        # Ejecutar clonación
        vm_id = await proxmox_client.clone(
            template_id=template_id,
            name=target_name,
            pool=f"workzone-{workzone_id}"
        )
        return [TextContent(
            type="text",
            text=json.dumps({"vm_id": vm_id, "status": "cloned"})
        )]

    elif name == "run_ansible_playbook":
        # Ejecutar playbook — SIEMPRE con validación previa
        playbook_content = arguments["playbook"]

        # Validar el playbook antes de ejecutar
        validation = validate_ansible_playbook(playbook_content)
        if not validation["valid"]:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Playbook rechazado por validación",
                    "issues": validation["issues"]
                })
            )]

        result = await ansible_runner.run(
            playbook=playbook_content,
            inventory=arguments.get("inventory"),
            timeout=300  # 5 minutos máximo
        )
        return [TextContent(
            type="text",
            text=json.dumps(result)
        )]
