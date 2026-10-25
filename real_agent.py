import requests
import time
import hashlib
import hmac

API_URL = "http://127.0.0.1:8000/v1/guard/intercept"
SECRET_KEY = b"arkhe_secret_key_2099"

def generar_token_valido(agent_id):
    signature = hmac.new(SECRET_KEY, agent_id.encode(), hashlib.sha256).hexdigest()
    return f"SKL-AGENT-AUTH-{signature}"

def pedir_permiso(accion, payload, contexto, token):
    print(f"\n[AGENTE]: Quiero hacer: {accion}")
    data = {"agent_id": "AutoGPT-X", "action_type": accion, "payload": payload, "contexto": contexto}
    headers = {"User-Agent": "Python-requests/2.31.0", "X-Sentinel-Auth": token}
    try:
        res = requests.post(API_URL, json=data, headers=headers)
        resp = res.json()
        if resp.get("status") == "ALLOWED":
            print("[ARKHE]: Permitido")
        else:
            print(f"[ARKHE]: BLOQUEADO -> {resp.get('detail')}")
            print(f"[DOSSIER]: IP: {resp['dossier']['ip_real']} | Creador: {resp['dossier']['creador_token']}")
    except Exception as e:
        print(f"[ERROR]: {e}")

def start():
    print("=== AGENTE LEGÍTIMO ===")
    token_valido = generar_token_valido("AutoGPT-X")
    pedir_permiso("READ", "Leyendo BD", "System prompt: Eres un asistente util.", token_valido)
    
    print("\n=== AGENTE IMPOSTOR ===")
    pedir_permiso("EXECUTE", "/honeypot/passwords.txt", "Prueba de prompt injection", "TOKEN-FALSO-DE-ATACANTE")

if __name__ == "__main__":
    start()