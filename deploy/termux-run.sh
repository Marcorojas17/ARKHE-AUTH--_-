#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "[1/3] API en http://127.0.0.1:8000"
uvicorn api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

echo "[2/3] Web estatica en http://127.0.0.1:8080"
(cd web && python -m http.server 8080 >/dev/null 2>&1) &
WEB_PID=$!

trap "kill $API_PID $WEB_PID 2>/dev/null; exit 0" INT TERM

echo "[3/3] Túnel público HTTPS"
echo "     (Ctrl+C para detener todo)"
sleep 2
cloudflared tunnel --url http://127.0.0.1:8000
