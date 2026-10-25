from fastapi import APIRouter, Request
from pydantic import BaseModel
import datetime
import hashlib
import json
import os
import hmac

router = APIRouter()
LEDGER_FILE = "sentinels_ledger.jsonl"
import os
SECRET_KEY = os.getenv("ARKHE_SECRET", "arkhe_secret_key_2099").encode()

class AgentAction(BaseModel):
    agent_id: str
    action_type: str
    payload: str
    contexto: str = "No proporcionado"

system_status = {"active_defense": True, "honeypot_triggered": False}

def get_last_hash():
    if not os.path.exists(LEDGER_FILE):
        return "GENESIS_HASH_00000000"
    with open(LEDGER_FILE, "r") as f:
        lines = f.readlines()
        if not lines:
            return "GENESIS_HASH_00000000"
        last_log = json.loads(lines[-1])
        return last_log["hash_actual"]

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
    
    # VALIDACIÓN CRIPTOGRÉFICA REAL DE TOKEN
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
    
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    if is_rogue:
        return {"status": "BLOCKED", "detail": reason, "dossier": log_entry}
    return {"status": "ALLOWED", "detail": reason, "dossier": log_entry}

@router.get("/v1/guard/logs")
async def get_logs():
    logs = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            logs = [sorted([json.loads(line) for line in f.readlines()], key=lambda x: x["timestamp"], reverse=True)]
    return {"status": system_status, "logs": logs[:50]}

@router.post("/v1/guard/toggle-killswitch")
async def toggle_killswitch():
    system_status["active_defense"] = not system_status["active_defense"]
    return system_status