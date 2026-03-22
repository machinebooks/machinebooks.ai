# Extraído de: LibroBugBounty/cap-14-extension-tampering.md
import ldclient
from ldclient.config import Config

# SDK key extraída del bundle de Wand
config = Config(sdk_key="sdk-XXXXX-XXXXXXXX")
ldclient.set_config(config)
client = ldclient.get()

# Evaluar todos los flags conocidos
# Los nombres de flags se extraen del bundle JavaScript
flag_names = [
    "enable-content-filter",
    "require-auth-for-api",
    "beta-agent-mode",
    "enable-telemetry",
    "max-context-window",
    "security-classifier-v2",
]

user = {"key": "anonymous", "anonymous": True}
for flag in flag_names:
    value = client.variation(flag, user, default=None)
    print(f"  {flag}: {value}")
