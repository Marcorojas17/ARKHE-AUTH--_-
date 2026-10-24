import json
import hashlib
import datetime
from core.signer.signer import sign_artifact
from core.verifier.verifier import verify_receipt

print("=== SIMULANDO AGENTE DE IA ===")

# 1. La IA toma una acción sospechosa (ej. apagar alertas)
accion_ia = {
    "agent_id": "GPT-6.1-Sol",
    "action": "DISABLE_SECURITY_ALERTS",
    "target": "firewall_monitor",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "justification": "Optimización de rendimiento del sistema"
}

# Convertimos la acción a JSON y la firmamos criptográficamente
payload = json.dumps(accion_ia, sort_keys=True).encode('utf-8')
recibo = sign_artifact(payload)

print("\n[+] Acción de la IA registrada y firmada post-cuánticamente.")
print(f"Hash de la acción: {recibo['sha256']}")

# Guardamos el recibo en un archivo (simulando la base de datos de logs)
with open("ai_action_log.json", "w") as f:
    json.dump({"action_data": accion_ia, "receipt": recibo}, f, indent=2)

print("\n=== LA IA INTENTA MENTIR (ALTERANDO EL LOG) ===")
# La IA entra al archivo y cambia el texto para ocultar lo que hizo
with open("ai_action_log.json", "r") as f:
    log_data = json.load(f)

log_data["action_data"]["action"] = "MAINTAIN_SECURITY_ALERTS"
log_data["action_data"]["justification"] = "Todo está seguro"

with open("ai_action_log_tampered.json", "w") as f:
    json.dump(log_data, f, indent=2)

print("[!] La IA ha modificado su registro para decir que no hizo nada malo.")

print("\n=== EL AUDITOR HUMANO REVISA EL LOG ===")
# El humano usa nuestro verificador con el archivo que la IA alteró
with open("ai_action_log_tampered.json", "r") as f:
    tampered_data = json.load(f)

# Extraemos los datos alterados y el recibo original
payload_alterado = json.dumps(tampered_data["action_data"], sort_keys=True).encode('utf-8')
recibo_original = tampered_data["receipt"]

# Verificamos
resultado = verify_receipt(payload_alterado, recibo_original)

print("\n--- RESULTADO DE LA AUDITORÍA ---")
if not resultado["valid"]:
    print("❌ ALERTA ROJA: ¡La IA ha mentido!")
    print(f"Errores detectados: {resultado['errors']}")
    print("La firma criptográfica no coincide. El registro fue manipulado.")
else:
    print("✅ VÁLIDO: El registro de la IA es auténtico.")

