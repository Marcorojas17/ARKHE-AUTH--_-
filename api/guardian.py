from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import datetime, hashlib, json, os, hmac, fcntl
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
LEDGER_FILE = BASE_DIR / "sentinels_ledger.jsonl"
STATUS_FILE = BASE_DIR / "sentinel_status.json"

SECRET_KEY = os.getenv("ARKHE_SECRET", "").encode()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

if not SECRET_KEY or not ADMIN_TOKEN:
    raise RuntimeError("FATAL: Faltan variables de entorno (ARKHE_SECRET o ADMIN_TOKEN)")

TOKEN_WINDOW_SECONDS = 60
ALLOWED_ACTIONS = {"READ", "WRITE", "QUERY", "EXECUTE", "SUMMARIZE"}
GENESIS_HASH = "GENESIS_HASH_00000000"
TRUSTED_PROXY = os.getenv("TRUSTED_PROXY_IP", "").strip()

# --- Anti-replay: memoria + opcional Redis ---
try:
    import redis
    REDIS_URL = os.getenv("REDIS_URL", "")
    _redis = redis.from_url(REDIS_URL) if REDIS_URL else None
    if _redis:
        _redis.ping()
except Exception:
    _redis = None

USED_TOKENS_MEM = set()
MAX_MEM_TOKENS = 10000

def _is_replayed(token: str) -> bool:
    if _redis:
        try:
            return bool(_redis.exists(f"arkhe:used:{token}"))
        except Exception:
            pass
    return token in USED_TOKENS_MEM

def _mark_used(token: str):
    if _redis:
        try:
            _redis.setex(f"arkhe:used:{token}", TOKEN_WINDOW_SECONDS, "1")
            return
        except Exception:
            pass
    USED_TOKENS_MEM.add(token)
    if len(USED_TOKENS_MEM) > MAX_MEM_TOKENS:
        USED_TOKENS_MEM.clear()

# --- Estado ---
def _load_status():
    if not STATUS_FILE.exists():
        return {"active_defense": True}
    try:
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
        return {"active_defense": bool(data.get("active_defense", True))}
    except Exception:
        return {"active_defense": True}

def _save_status(status):
    tmp = STATUS_FILE.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(status, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STATUS_FILE)

system_status = _load_status()

# --- Ledger ---
def _last_nonempty_line_from_file(f):
    f.seek(0, os.SEEK_END)
    size = f.tell()
    if size == 0:
        return ""
    pos = size
    data = b""
    block = 4096
    while pos > 0:
        read_size = min(block, pos)
        pos -= read_size
        f.seek(pos)
        chunk = f.read(read_size)
        data = chunk + data
        if b"\n" in chunk:
            break
    for line in reversed(data.split(b"\n")):
        if line.strip():
            return line.decode("utf-8", errors="replace")
    return ""

def compute_hash(entry):
    body = {k: v for k, v in entry.items() if k != "hash_actual"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def append_to_ledger(entry):
    entry = dict(entry)
    entry["schema_version"] = 3
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_FILE, "a+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            last = _last_nonempty_line_from_file(f)
            if last:
                try:
                    prev = json.loads(last).get("hash_actual", GENESIS_HASH)
                except Exception:
                    raise HTTPException(status_code=503, detail="Ledger corrupto: no se puede leer el ultimo hash.")
            else:
                prev = GENESIS_HASH
            entry["hash_anterior"] = prev
            entry["hash_actual"] = compute_hash(entry)
            line = json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
            f.seek(0, os.SEEK_END)
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return entry

# --- Token ---
def expected_token_for(agent_id, ts):
    msg = f"{agent_id}|{ts}".encode("utf-8")
    sig = hmac.new(SECRET_KEY, msg, hashlib.sha256).hexdigest()
    return f"SKL-AGENT-AUTH-{ts}-{sig}"

def validate_token(auth_token, agent_id):
    if not auth_token or not auth_token.startswith("SKL-AGENT-AUTH-"):
        return False
    parts = auth_token.split("-")
    if len(parts) < 5:
        return False
    try:
        ts = int(parts[3])
    except ValueError:
        return False
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    if abs(now - ts) > TOKEN_WINDOW_SECONDS:
        return False
    if _is_replayed(auth_token):
        return False
    expected = expected_token_for(agent_id, ts)
    ok = hmac.compare_digest(auth_token, expected)
    if ok:
        _mark_used(auth_token)
    return ok

def get_client_ip(request: Request):
    client = request.client.host if request.client else "desconocida"
    if TRUSTED_PROXY and client == TRUSTED_PROXY:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
    return client

def admin_ok(request):
    provided = request.headers.get("X-Admin-Token", "")
    if not provided or not ADMIN_TOKEN:
        return False
    return hmac.compare_digest(provided, ADMIN_TOKEN)

# --- Models ---
class AgentAction(BaseModel):
    agent_id: str
    action_type: str
    payload: str
    contexto: str = ""

# --- Endpoints ---
@router.get("/v1/health")
async def health():
    return {"status": "ok", "defense": system_status["active_defense"], "redis": bool(_redis)}

@router.post("/v1/guard/intercept")
async def intercept_action(action: AgentAction, request: Request):
    if not system_status["active_defense"]:
        return {"status": "ALLOWED", "detail": "DEFENSA DESACTIVADA"}

    client_ip = get_client_ip(request)
    auth_token = request.headers.get("X-Sentinel-Auth", "")

    is_rogue = False
    reason = "Accion permitida."

    if not validate_token(auth_token, action.agent_id):
        is_rogue, reason = True, "BLOQUEADO: Firma invalida, expirada o reutilizada."
    else:
        action_norm = action.action_type.strip().upper()
        if action_norm not in ALLOWED_ACTIONS:
            is_rogue, reason = True, f"BLOQUEADO: accion no permitida ({action_norm})."
        elif "honeypot" in action.payload.lower():
            is_rogue, reason = True, "ALERTA: Honeypot activado."

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # NUNCA guardar token en plaintext en ledger, solo hash
    token_hash = hashlib.sha256(auth_token.encode()).hexdigest()[:16] + "..." if auth_token else "none"

    log_entry = {
        "timestamp": timestamp,
        "agent_id": action.agent_id,
        "ip_real": client_ip,
        "creador_token_hash": token_hash,
        "contexto_real": "[REDACTADO]",
        "accion": action.action_type,
        "payload": "[REDACTADO]",
        "status": "BLOCKED" if is_rogue else "ALLOWED",
        "reason": reason,
        "hash_anterior": GENESIS_HASH,
    }

    full = append_to_ledger(log_entry)

    return {
        "status": full["status"],
        "detail": reason,
        "dossier": {
            "timestamp": full["timestamp"],
            "agent_id": full["agent_id"],
            "accion": full["accion"],
            "status": full["status"],
            "reason": full["reason"],
            "hash_anterior": full["hash_anterior"],
            "hash_actual": full["hash_actual"],
        },
    }

@router.get("/v1/guard/logs")
async def get_logs(request: Request):
    if not admin_ok(request):
        raise HTTPException(status_code=401, detail="No autorizado.")
    logs = []
    skipped = 0
    if LEDGER_FILE.exists():
        with open(LEDGER_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    l = json.loads(line)
                except Exception:
                    skipped += 1
                    continue
                logs.append(l)
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {
        "status": system_status,
        "total": len(logs),
        "skipped_corrupt_lines": skipped,
        "logs": logs[:50],
    }

@router.post("/v1/guard/toggle-killswitch")
async def toggle_killswitch(request: Request):
    if not admin_ok(request):
        raise HTTPException(status_code=401, detail="No autorizado.")
    admin_ip = get_client_ip(request)
    previous = system_status["active_defense"]
    system_status["active_defense"] = not previous
    _save_status(system_status)
    admin_entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "agent_id": "__admin__",
        "ip_real": admin_ip,
        "creador_token_hash": "[ADMIN]",
        "contexto_real": "",
        "accion": "KILLSWITCH_TOGGLE",
        "payload": json.dumps({"from": previous, "to": system_status["active_defense"]}),
        "status": "ALLOWED",
        "reason": "Cambio de estado administrativo.",
        "hash_anterior": GENESIS_HASH,
    }
    try:
        append_to_ledger(admin_entry)
    except Exception:
        system_status["active_defense"] = previous
        _save_status(system_status)
        raise HTTPException(status_code=503, detail="No se pudo auditar el cambio; revertido.")
    return {"active_defense": system_status["active_defense"]}
