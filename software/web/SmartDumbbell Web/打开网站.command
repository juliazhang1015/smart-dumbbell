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
/usr/bin/python3 server.py &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null' EXIT
while ! ready; do
  kill -0 "$server_pid" 2>/dev/null || exit 1
  sleep 0.5
done
/usr/bin/open "$url/"
wait "$server_pid"
