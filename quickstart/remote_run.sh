#!/usr/bin/env bash
# Run the quickstart on a remote GPU machine over ssh, inside tmux, and fetch
# the results. Usage:
#   ./remote_run.sh HOST check            # disk, memory, GPU, tools on HOST
#   ./remote_run.sh HOST start [ARGS...]  # clone, set up and run in tmux; ARGS go to run_quickstart.py
#   ./remote_run.sh HOST status           # is the job running? last lines of its log
#   ./remote_run.sh HOST fetch            # copy results/ to ./results-HOST/
# HOST is any name ssh understands: a Tailscale machine name (MagicDNS) such
# as gpu-box-1, or a Host entry in ~/.ssh/config. See tutorial lesson 3.
# Override with environment variables: REMOTE_DIR (default geneformer-starter),
# SESSION (default gf), REPO_URL. Values must not contain quotes. The log of
# setup and run is REMOTE_DIR/quickstart/run.log; uv is looked up in ~/.local/bin too.
set -euo pipefail

REMOTE_DIR="${REMOTE_DIR:-geneformer-starter}"
SESSION="${SESSION:-gf}"
REPO_URL="${REPO_URL:-https://github.com/Kays3/geneformer-petadimension-starter.git}"

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ $# -ge 2 ] || usage
HOST="$1"; ACTION="$2"; shift 2

# Arguments for run_quickstart.py are passed through a quoted string so they
# survive the remote shell.
quoted_args=""
for a in "$@"; do quoted_args+=" $(printf '%q' "$a")"; done

case "$ACTION" in
  check)
    ssh "$HOST" 'export PATH="$HOME/.local/bin:$PATH"; hostname; echo "--- disk"; df -h ~ | tail -1; echo "--- memory (GB)"; free -g | head -2;
      echo "--- GPU"; (nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader 2>/dev/null || echo "no NVIDIA GPU found (the run falls back to the CPU)");
      echo "--- tools"; for t in git curl tmux uv; do command -v $t >/dev/null && echo "$t: ok" || echo "$t: MISSING"; done'
    ;;
  start)
    ssh "$HOST" "set -e
      export PATH=\"\$HOME/.local/bin:\$PATH\"
      command -v tmux >/dev/null || { echo 'tmux is not installed on $HOST' >&2; exit 1; }
      tmux has-session -t '$SESSION' 2>/dev/null && { echo 'A tmux session named $SESSION is already running; use status' >&2; exit 1; }
      if [ -d '$REMOTE_DIR/.git' ]; then git -C '$REMOTE_DIR' pull --ff-only || echo 'Could not update the existing checkout; running what is there.'; else git clone '$REPO_URL' '$REMOTE_DIR'; fi
      tmux new-session -d -s '$SESSION' \"cd '$REMOTE_DIR/quickstart' && { ./setup.sh && uv run python run_quickstart.py$quoted_args; } 2>&1 | tee run.log\"
      echo 'Started in tmux session $SESSION on $HOST.'"
    echo "Check on it with: ./remote_run.sh $HOST status"
    ;;
  status)
    ssh "$HOST" "if tmux has-session -t '$SESSION' 2>/dev/null; then echo RUNNING; else echo 'NOT RUNNING (finished or never started)'; fi
      tail -n 8 '$REMOTE_DIR/quickstart/run.log' 2>/dev/null || echo 'no log yet'"
    ;;
  fetch)
    mkdir -p "results-$HOST"
    scp -r "$HOST:$REMOTE_DIR/quickstart/results/." "results-$HOST/"
    echo "Copied to results-$HOST/"
    ;;
  *) usage ;;
esac
