#!/usr/bin/env python3
"""
Live visualizer for the Mininet V0.1 traffic.

It starts tcpdump, parses IP packet lines, and serves a tiny browser dashboard.
"""

import argparse
import json
import queue
import re
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOSTS = {f"10.0.0.{i}": f"h{i}" for i in range(1, 9)}
PACKET_QUEUE = queue.Queue(maxsize=500)
RECENT_PACKETS = deque(maxlen=400)
RECENT_LOCK = threading.Lock()
TCPDUMP_PROCESS = None
DEBUG = False

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simulation V0.1 Traffic</title>
  <style>
    :root {
      color-scheme: dark;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #111317;
      color: #eef2f6;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      border-bottom: 1px solid #2b3038;
      background: #171a20;
    }
    h1 {
      margin: 0;
      font-size: 16px;
      font-weight: 650;
    }
    #stats {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: #bac4d0;
    }
    main {
      display: grid;
      grid-template-columns: minmax(560px, 1fr) 340px;
      min-height: 0;
    }
    #stage {
      position: relative;
      overflow: hidden;
      background: #111317;
    }
    svg {
      width: 100%;
      height: 100%;
      display: block;
    }
    .link {
      stroke: #38414d;
      stroke-width: 2;
    }
    .host {
      fill: #1d232c;
      stroke: #6a7481;
      stroke-width: 2;
    }
    .switch {
      fill: #263241;
      stroke: #8ea1b5;
      stroke-width: 2;
    }
    .label {
      fill: #eef2f6;
      font-size: 13px;
      text-anchor: middle;
      dominant-baseline: middle;
      pointer-events: none;
    }
    .packet {
      stroke: white;
      stroke-width: 1.5;
    }
    aside {
      border-left: 1px solid #2b3038;
      background: #171a20;
      min-height: 0;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    aside h2 {
      margin: 0;
      padding: 12px 14px;
      font-size: 14px;
      border-bottom: 1px solid #2b3038;
    }
    #events {
      overflow: auto;
      padding: 8px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
    }
    .event {
      padding: 7px 8px;
      border-bottom: 1px solid #242a32;
      color: #d7dee7;
      white-space: nowrap;
    }
    .ICMP { fill: #55c2ff; color: #55c2ff; }
    .TCP { fill: #ffcf5a; color: #ffcf5a; }
    .UDP { fill: #72e28b; color: #72e28b; }
    .IP { fill: #d08cff; color: #d08cff; }
  </style>
</head>
<body>
  <header>
    <h1>Simulation V0.1 Traffic</h1>
    <div id="stats">
      <span>Packets: <strong id="count">0</strong></span>
      <span>Last: <strong id="last">waiting</strong></span>
      <span>Status: <strong id="status">loading</strong></span>
    </div>
  </header>
  <main>
    <section id="stage">
      <svg id="svg" viewBox="0 0 900 640" aria-label="Network traffic map"></svg>
    </section>
    <aside>
      <h2>Live packets</h2>
      <div id="events"></div>
    </aside>
  </main>
  <script>
    const svg = document.getElementById("svg");
    const events = document.getElementById("events");
    const countEl = document.getElementById("count");
    const lastEl = document.getElementById("last");
    const statusEl = document.getElementById("status");
    const positions = {};
    let count = 0;
    let lastSeen = 0;

    function el(name, attrs = {}) {
      const node = document.createElementNS("http://www.w3.org/2000/svg", name);
      for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
      return node;
    }

    function drawTopology() {
      const center = { x: 450, y: 320 };
      positions.s1 = center;
      for (let i = 1; i <= 8; i++) {
        const angle = (-90 + (i - 1) * 45) * Math.PI / 180;
        positions[`h${i}`] = {
          x: center.x + Math.cos(angle) * 245,
          y: center.y + Math.sin(angle) * 210,
        };
      }

      for (let i = 1; i <= 8; i++) {
        const p = positions[`h${i}`];
        svg.appendChild(el("line", { x1: center.x, y1: center.y, x2: p.x, y2: p.y, class: "link" }));
      }

      svg.appendChild(el("rect", {
        x: center.x - 38, y: center.y - 24, width: 76, height: 48, rx: 7, class: "switch"
      }));
      svg.appendChild(el("text", { x: center.x, y: center.y, class: "label" })).textContent = "s1";

      for (let i = 1; i <= 8; i++) {
        const p = positions[`h${i}`];
        svg.appendChild(el("circle", { cx: p.x, cy: p.y, r: 28, class: "host" }));
        svg.appendChild(el("text", { x: p.x, y: p.y, class: "label" })).textContent = `h${i}`;
      }
    }

    function animatePacket(packet) {
      const src = positions[packet.src_host];
      const dst = positions[packet.dst_host];
      if (!src || !dst) return;

      const dot = el("circle", {
        cx: src.x,
        cy: src.y,
        r: 8,
        class: `packet ${packet.protocol}`,
      });
      svg.appendChild(dot);

      const via = positions.s1;
      const path = [src, via, dst];
      let segment = 0;
      const started = performance.now();
      const duration = 950;

      function frame(now) {
        const progress = Math.min((now - started) / duration, 1);
        const scaled = progress * 2;
        segment = scaled < 1 ? 0 : 1;
        const local = segment === 0 ? scaled : scaled - 1;
        const a = path[segment];
        const b = path[segment + 1];
        dot.setAttribute("cx", a.x + (b.x - a.x) * local);
        dot.setAttribute("cy", a.y + (b.y - a.y) * local);
        dot.setAttribute("opacity", String(1 - progress * 0.35));
        if (progress < 1) requestAnimationFrame(frame);
        else dot.remove();
      }
      requestAnimationFrame(frame);
    }

    function addEvent(packet) {
      count += 1;
      countEl.textContent = String(count);
      lastEl.textContent = `${packet.src_host} -> ${packet.dst_host}`;

      const line = document.createElement("div");
      line.className = `event ${packet.protocol}`;
      line.textContent = `${packet.protocol.padEnd(4)} ${packet.src_host} -> ${packet.dst_host}`;
      events.prepend(line);
      while (events.children.length > 80) events.lastChild.remove();
    }

    drawTopology();

    async function poll() {
      try {
        const response = await fetch(`/packets?since=${lastSeen}`, { cache: "no-store" });
        const packets = await response.json();
        statusEl.textContent = "connected";
        for (const packet of packets) {
          lastSeen = Math.max(lastSeen, packet.id);
          addEvent(packet);
          animatePacket(packet);
        }
      } catch (error) {
        statusEl.textContent = "connection lost";
      } finally {
        setTimeout(poll, 250);
      }
    }

    poll();
  </script>
</body>
</html>
"""


def parse_tcpdump_line(line):
    if " IP " not in line and not line.startswith("IP "):
        return None

    ips = re.findall(r"10\.0\.0\.\d+", line)
    if len(ips) < 2:
        return None

    src_ip, dst_ip = ips[0], ips[1]
    src_host = HOSTS.get(src_ip)
    dst_host = HOSTS.get(dst_ip)
    if not src_host or not dst_host or src_host == dst_host:
        return None

    if "ICMP" in line:
        protocol = "ICMP"
    elif "UDP" in line:
        protocol = "UDP"
    elif "Flags" in line or re.search(r"\.\d+ > .*\.\d+:", line):
        protocol = "TCP"
    else:
        protocol = "IP"

    return {
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_host": src_host,
        "dst_host": dst_host,
        "protocol": protocol,
        "time": time.time(),
    }


def run_tcpdump(interface):
    global TCPDUMP_PROCESS
    packet_id = 0
    command = ["tcpdump", "-l", "-nn", "-i", interface, "net", "10.0.0.0/24"]
    print("Running:", " ".join(command), flush=True)
    TCPDUMP_PROCESS = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    for line in TCPDUMP_PROCESS.stdout:
        if DEBUG:
            print(line.rstrip(), flush=True)
        packet = parse_tcpdump_line(line)
        if packet:
            packet_id += 1
            packet["id"] = packet_id
            print(
                f"{packet['protocol']} {packet['src_host']} -> {packet['dst_host']}",
                flush=True,
            )
            with RECENT_LOCK:
                RECENT_PACKETS.append(packet)
            try:
                PACKET_QUEUE.put_nowait(packet)
            except queue.Full:
                pass


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())
            return

        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            while True:
                packet = PACKET_QUEUE.get()
                data = f"data: {json.dumps(packet)}\\n\\n"
                try:
                    self.wfile.write(data.encode())
                    self.wfile.flush()
                except BrokenPipeError:
                    return

        if self.path.startswith("/packets"):
            since = 0
            if "?" in self.path:
                query = self.path.split("?", 1)[1]
                for part in query.split("&"):
                    key, _, value = part.partition("=")
                    if key == "since":
                        try:
                            since = int(value)
                        except ValueError:
                            since = 0

            with RECENT_LOCK:
                packets = [packet for packet in RECENT_PACKETS if packet["id"] > since]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(packets).encode())
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    global DEBUG
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="any")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    DEBUG = args.debug

    threading.Thread(target=run_tcpdump, args=(args.interface,), daemon=True).start()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Open http://{args.host}:{args.port}", flush=True)
    print(f"Listening to tcpdump on {args.interface}", flush=True)
    try:
        server.serve_forever()
    finally:
        if TCPDUMP_PROCESS:
            TCPDUMP_PROCESS.terminate()


if __name__ == "__main__":
    main()
