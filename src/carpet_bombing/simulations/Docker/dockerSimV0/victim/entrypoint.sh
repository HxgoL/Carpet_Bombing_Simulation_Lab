#!/bin/sh
set -eu

MODE="${VICTIM_MODE:-nginx}"

case "$MODE" in
  nginx)
    echo "Starting nginx victim"
    nginx -g "daemon off;"
    ;;
  iperf3)
    echo "Starting iperf3 victim"
    iperf3 -s
    ;;
  python_http)
    echo "Starting Python HTTP victim"
    python -m http.server 80
    ;;
  *)
    echo "Unknown VICTIM_MODE=$MODE" >&2
    exit 1
    ;;
esac