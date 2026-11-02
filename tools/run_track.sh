#!/bin/zsh
# Run one pass-3 track in a fresh headless Claude Code session; retry on transient API/network failure.
# Usage: tools/run_track.sh U|R|C
cd "$(dirname "$0")/.."
export POLICY_TEXT_DIR="$PWD/.cache/text" CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0
track=$1; t=${track:l}
for attempt in 1 2 3; do
  log="logs/pass3_${t}_run_$(date +%H%M%S).json"
  claude -p "Read tools/PASS3_BRIEF.md in the current directory, including the Continuation rules at the end, and carry out Track ${track} completely. The fetch helper's cache directory is set by the POLICY_TEXT_DIR environment variable." \
    --permission-mode acceptEdits \
    --allowedTools "WebSearch" "WebFetch" "Read" "Write" "Edit" "Glob" "Grep" "Agent" "Bash(python3:*)" "Bash(curl:*)" "Bash(ls:*)" "Bash(cat:*)" "Bash(head:*)" "Bash(wc:*)" "Bash(mkdir:*)" "Bash(grep:*)" \
    --output-format json < /dev/null > "$log" 2>> "logs/pass3_${t}_err.txt"
  if python3 -c "import json,sys; r=json.load(open('$log')); sys.exit(1 if r.get('is_error') else 0)" 2>/dev/null; then
    echo "track $track done ($log)"; exit 0
  fi
  echo "track $track attempt $attempt failed; retrying in 60s"; sleep 60
done
echo "track $track failed 3 times"; exit 1
