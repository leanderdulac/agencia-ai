#!/usr/bin/env bash
# Khabs — unified local site + automation API on :8787
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT="${KHABS_PORT:-8787}"
PIDFILE="${ROOT}/local-api/.server.pid"
LOGFILE="${ROOT}/local-api/server.log"

cd "$ROOT"

# Soft stop: only our previous pid if still listening on PORT
if [[ -f "$PIDFILE" ]]; then
  OLD="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ -n "${OLD}" ]] && kill -0 "$OLD" 2>/dev/null; then
    # only kill if it looks like our server
    if ps -p "$OLD" -o args= 2>/dev/null | grep -q "local-api/server.py"; then
      kill "$OLD" 2>/dev/null || true
      sleep 0.4
    fi
  fi
  rm -f "$PIDFILE"
fi

# If something else already serves 8787, do not kill aggressively — refuse
if command -v ss >/dev/null 2>&1; then
  if ss -ltn "( sport = :$PORT )" 2>/dev/null | grep -q ":$PORT"; then
    echo "Porta $PORT já em uso. Pare o processo manualmente ou use KHABS_PORT=8788 ./start-local.sh"
    exit 1
  fi
elif command -v lsof >/dev/null 2>&1; then
  if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Porta $PORT já em uso. Pare o processo manualmente ou use KHABS_PORT=8788 ./start-local.sh"
    exit 1
  fi
fi

export KHABS_AGENCIA="${KHABS_AGENCIA:-$ROOT/agencia-ai}"
export KHABS_PORT="$PORT"

nohup python3 "$ROOT/local-api/server.py" >>"$LOGFILE" 2>&1 &
echo $! >"$PIDFILE"
sleep 0.5

if ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Falha ao iniciar. Veja $LOGFILE"
  exit 1
fi

cat <<EOF

★ Khabs local stack rodando
  Site + API:  http://127.0.0.1:${PORT}/
  Diagnóstico: http://127.0.0.1:${PORT}/qualificar.html
  Contato:     http://127.0.0.1:${PORT}/contato.html
  Portal:      http://127.0.0.1:${PORT}/portal.html
  Ops board:   http://127.0.0.1:${PORT}/ops.html
  Health:      http://127.0.0.1:${PORT}/api/health

  PID: $(cat "$PIDFILE")  ·  log: $LOGFILE
  CRM: \$KHABS_AGENCIA/crm-lite/

  (Alternativa: site estático em :8080 + API :8787 — prefira este processo único.)

EOF
