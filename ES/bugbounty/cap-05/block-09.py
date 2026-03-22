# Extraído de: LibroBugBounty/cap-05-asar-tampering.md
# CÃ¡lculo correcto de padding
header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
json_size = len(header_json)
padding = (4 - (json_size % 4)) % 4  # 0, 1, 2 o 3 bytes

# El pickle header completo:
# 4 bytes: tamaÃ±o del pickle (siempre 4)
# 4 bytes: json_size + padding + 4
# 4 bytes: json_size + padding
# 4 bytes: json_size
# N bytes: header JSON
# P bytes: padding (0-3 bytes nulos)
# DespuÃ©s: zona de datos
