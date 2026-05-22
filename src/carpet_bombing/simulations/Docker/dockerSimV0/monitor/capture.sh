#!/bin/sh
set -eu

SCENARIO="${1:-capture}"
INTERFACE="${INTERFACE:-eth0}"
TS="$(date -u +"%Y%m%dT%H%M%SZ")"

PCAP_DIR="data/pcaps"
LOG_DIR="data/logs"

mkdir -p "$PCAP_DIR" "$LOG_DIR"

OUT="$PCAP_DIR/${SCENARIO}_${TS}.pcap"
LOG="$LOG_DIR/${SCENARIO}_${TS}.log"

echo "Starting capture scenario=$SCENARIO interface=$INTERFACE output=$OUT" | tee "$LOG"

ln -sf "$(basename "$OUT")" "$PCAP_DIR/latest.pcap"

tcpdump -i "$INTERFACE" -nn -s 0 -w "$OUT" 2>&1 | tee -a "$LOG"