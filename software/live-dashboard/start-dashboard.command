#!/bin/zsh
cd "${0:A:h}" || exit 1
url=http://127.0.0.1:8001
ready() {
  /usr/bin/curl -fsS --max-time 1 "$url/live" 2>/dev/null | /usr/bin/grep -q '"sequence"'
}
if ready; then
  /usr/bin/open "$url/"
  exit $?
fi
# The AI coach needs the Claude API key. A .command file does not read ~/.zshrc, so fetch the key
# from an interactive shell if it is not already set (the value is never printed).
if [[ -z "$ANTHROPIC_API_KEY" ]]; then
  export ANTHROPIC_API_KEY="$(/bin/zsh -ic 'print -r -- "SDKEY=$ANTHROPIC_API_KEY"' 2>/dev/null | /usr/bin/sed -n 's/^SDKEY=//p' | tail -n 1)"
  [[ -z "$ANTHROPIC_API_KEY" ]] && unset ANTHROPIC_API_KEY && echo "No ANTHROPIC_API_KEY found: the dashboard runs, the AI coach stays off."
fi
# The Anthropic SDK needs Python 3.10+, so run through uv (system python3 is 3.9).
uv=""
for candidate in /opt/homebrew/bin/uv /usr/local/bin/uv "$HOME/.local/bin/uv"; do
  [[ -x "$candidate" ]] && uv="$candidate" && break
done
if [[ -n "$uv" ]]; then
  "$uv" run --quiet --python 3.12 --with anthropic python server.py &
else
  echo "uv not found: starting without the AI coach (install with: brew install uv)."
  /usr/bin/python3 server.py &
fi
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null' EXIT
while ! ready; do
  kill -0 "$server_pid" 2>/dev/null || exit 1
  sleep 0.5
done
/usr/bin/open "$url/"
wait "$server_pid"
