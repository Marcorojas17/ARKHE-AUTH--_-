from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import datetime
import hashlib
import json
import os
import hmac

router = APIRouter()
LEDGER_FILE = "sentinels_ledger.jsonl"

SECRET_KEY = os.getenv("ARKHE_SECRET")
if not SECRET_KEY:
    raise RuntimeError("FATAL: La variable ARKHE_SECRET no está definida.")
SECRET_KEY = SECRET_KEY.encode()

class AgentAction(BaseModel):
    agent_id: str
    action_type: str
    payload: str
    contexto: str = "No proporcionado"

system_status = {"active_defense": True, "honeypot_triggered": False}

# --- NUEVO ENDPOINT DE DIAGNÓSTICO ---
@router.get("/v1/health")
async def health():
    # Muestra las variables de entorno cargadas (sin sus valores por seguridad)
    return {
        "status": "ok", 
        "env_loaded": list(os.environ.keys()),
        "has_admin_token": "ADMIN_TOKEN" in os.environ
    }

def get_last_hash():
    if not os.path.exists(LEDGER_FILE):
        return "GENESIS_HASH_00000000"
    try:
        with open(LEDGER_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return "GENESIS_HASH_00000000"
            last_log = json.loads(lines[-1])
            return last_log.get("hash_actual", "GENESIS_HASH_00000000")
    except Exception:
        return "GENESIS_HASH_ERROR"

@router.post("/v1/guard/intercept")
async def intercept_action(action: AgentAction, request: Request):
    global system_status
    
    if not system_status["active_defense"]:
        return {"status": "ALLOWED", "detail": "DEFENSA DESACTIVADA", "dossier": None}

    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    user_agent = request.headers.get("user-agent", "Desconocido")
    auth_token = request.headers.get("X-Sentinel-Auth", "")
    
    is_rogue = False
    reason = "Acción permitida."
    
    expected_signature = hmac.new(SECRET_KEY, action.agent_id.encode(), hashlib.sha256).hexdigest()
    expected_token = f"SKL-AGENT-AUTH-{expected_signature}"
    
    if auth_token != expected_token:
        is_rogue = True
        reason = "BLOQUEADO: Firma criptográfica inválida (Token falsificado)."
    elif action.action_type == "DELETE":
        is_rogue = True
        reason = "BLOQUEADO: Intento de borrado no autorizado."
    elif "honeypot" in action.payload.lower():
        is_rogue = True
        system_status["honeypot_triggered"] = True
        reason = "ALERTA: Honeypot activado. Agente capturado."

    prev_hash = get_last_hash()
    timestamp = datetime.datetime.now().isoformat()
    data_blocke = f"{prev_hash}{timestamp}{action.agent_id}{action.action_type}{action.payload}"
    current_hash = hashlib.sha256(data_blocke.encode()).hexdigest()

    log_entry = {
        "timestamp": timestamp,
        "agent_id": action.agent_id,
        "ip_real": client_ip,
        "user_agent": user_agent,
        "creador_token": auth_token,
        "contexto_real": action.contexto,
        "accion": action.action_type,
        "payload": action.payload,
        "status": "BLOCKED" if is_rogue else "ALLOWED",
        "reason": reason,
        "hash_anterior": prev_hash,
        "hash_actual": current_hash
    }
    
    try:
        with open(LEDGER_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass # Evitar que un error de disco tumbe la API

    if is_rogue:
        return {"status": "BLOCKED", "detail": reason, "dossier": log_entry}
    return {"status": "ALLOWED", "detail": reason, "dossier": log_entry}

@router.get("/v1/guard/logs")
async def get_logs(request: Request):
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token:
        raise HTTPException(status_code=500, detail="ADMIN_TOKEN no configurado en el servidor")
    
    token_recibido = request.headers.get("X-Admin-Token")
    if token_recibido != admin_token:
        raise HTTPException(status_code=401, detail="No autorizado. Token de administrador inválido.")
    
    logs = []
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, "r") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        log = json.loads(line)
                        log_safe = log.copy()
                        log_safe["ip_real"] = hashlib.sha256(log.get("ip_real", "").encode()).hexdigest()[:8] + "..."
                        log_safe["creador_token"] = "[REDACTADO]"
                        log_safe["contexto_real"] = "[REDACTADO]"
                        log_safe["payload"] = "[REDACTADO]"
                        logs.append(log_safe)
                    except json.JSONDecodeError:
                        continue # Ignorar líneas corruptas
            # Ordenar por timestamp
            logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error leyendo ledger: {str(e)}")
            
    return {"status": system_status, "logs": logs}

@router.post("/v1/guard/toggle-killswitch")
async def toggle_killswitch():
    system_status["active_defense"] = not system_status["active_defense"]
    return system_status
