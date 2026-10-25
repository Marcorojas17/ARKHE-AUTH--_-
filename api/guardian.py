from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import datetime, hashlib, json, os, hmac

router = APIRouter()
LEDGER_FILE = "sentinels_ledger.jsonl"
SECRET_KEY = os.getenv("ARKHE_SECRET", "").encode()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

if not SECRET_KEY or not ADMIN_TOKEN:
    raise RuntimeError("FATAL: Faltan variables de entorno (ARKHE_SECRET o ADMIN_TOKEN)")

class AgentAction(BaseModel):
    agent_id: str
    action_type: str
    payload: str
    contexto: str = "No proporcionado"

system_status = {"active_defense": True}

def get_last_hash():
    if not os.path.exists(LEDGER_FILE): return "GENESIS_HASH_00000000"
    try:
        with open(LEDGER_FILE, "r") as f:
            lines = f.readlines()
            if not lines: return "GENESIS_HASH_00000000"
            return json.loads(lines[-1]).get("hash_actual", "GENESIS_HASH_00000000")
    except Exception: return "GENESIS_HASH_ERROR"

@router.get("/v1/health")
async def health():
    return {"status": "ok", "env_loaded": "ARKHE_SECRET" in os.environ, "has_admin_token": "ADMIN_TOKEN" in os.environ}

@router.post("/v1/guard/intercept")
async def intercept_action(action: AgentAction, request: Request):
    if not system_status["active_defense"]:
        return {"status": "ALLOWED", "detail": "DEFENSA DESACTIVADA"}

    client_ip = request.headers.get("X-Forwarded-For", request.client.host)
    auth_token = request.headers.get("X-Sentinel-Auth", "")
    expected_token = f"SKL-AGENT-AUTH-{hmac.new(SECRET_KEY, action.agent_id.encode(), hashlib.sha256).hexdigest()}"
    
    is_rogue = False
    reason = "Acción permitida."
    
    if auth_token != expected_token:
        is_rogue, reason = True, "BLOQUEADO: Firma inválida."
    elif action.action_type == "DELETE":
        is_rogue, reason = True, "BLOQUEADO: Borrado no autorizado."
    elif "honeypot" in action.payload.lower():
        is_rogue, reason = True, "ALERTA: Honeypot activado."

    prev_hash = get_last_hash()
    timestamp = datetime.datetime.now().isoformat()
    current_hash = hashlib.sha256(f"{prev_hash}{timestamp}{action.agent_id}{action.action_type}".encode()).hexdigest()

    log_entry = {
        "timestamp": timestamp, "agent_id": action.agent_id, "ip_real": client_ip,
        "creador_token": auth_token, "contexto_real": action.contexto,
        "accion": action.action_type, "payload": action.payload,
        "status": "BLOCKED" if is_rogue else "ALLOWED", "reason": reason,
        "hash_anterior": prev_hash, "hash_actual": current_hash
    }
    
    with open(LEDGER_FILE, "a") as f: f.write(json.dumps(log_entry) + "\n")
    return {"status": "BLOCKED" if is_rogue else "ALLOWED", "detail": reason, "dossier": log_entry}

@router.get("/v1/guard/logs")
async def get_logs(request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado.")
    
    logs = []
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            for line in f:
                try:
                    l = json.loads(line)
                    l["ip_real"] = hashlib.sha256(l.get("ip_real", "").encode()).hexdigest()[:8] + "..."
                    l["creador_token"] = "[REDACTADO]"
                    l["contexto_real"] = "[REDACTADO]"
                    l["payload"] = "[REDACTADO]"
                    logs.append(l)
                except: continue
    return {"status": system_status, "logs": sorted(logs, key=lambda x: x.get("timestamp",""), reverse=True)[:50]}

@router.post("/v1/guard/toggle-killswitch")
async def toggle_killswitch(request: Request):
    if request.headers.get("X-Admin-Token") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado.")
    system_status["active_defense"] = not system_status["active_defense"]
    return system_status
