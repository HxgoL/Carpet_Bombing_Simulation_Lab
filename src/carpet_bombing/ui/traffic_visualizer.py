import argparse
import json
import queue
import re
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PACKET_QUEUE = queue.Queue(maxsize=500)
RECENT_PACKETS = deque(maxlen=400)
RECENT_LOCK = threading.Lock()
DEDUP_CACHE = {}
TCPDUMP_PROCESS = None
DEBUG = False
HOSTS = {}
HTML = ""
CURRENT_PACKET_ID = 0


def build_v0_1_topology():
    hosts = {f"10.0.0.{i}": f"h{i}" for i in range(1, 9)}
    nodes = [{"name": "s1", "x": 450, "y": 320, "type": "switch"}]

    for i in range(1, 9):
        angle = (-90 + (i - 1) * 45) * 3.14159 / 180
        nodes.append({
            "name": f"h{i}",
            "x": 450 + __import__("math").cos(angle) * 245,
            "y": 320 + __import__("math").sin(angle) * 210,
            "type": "host",
        })

    links = [["s1", f"h{i}"] for i in range(1, 9)]
    return "Simulation V0.1 Traffic", hosts, nodes, links


def build_v1_topology():
    hosts = {
        "10.0.1.1": "a1",
        "10.0.1.254": "gw",
        "10.0.0.254": "gw",
    }
    hosts.update({f"10.0.0.{i}": f"h{i}" for i in range(1, 9)})

    nodes = [
        {"name": "a1", "x": 130, "y": 320, "type": "attacker"},
        {"name": "s1", "x": 280, "y": 320, "type": "switch"},
        {"name": "gw", "x": 450, "y": 320, "type": "gateway"},
        {"name": "s2", "x": 620, "y": 320, "type": "switch"},
    ]

    for i in range(1, 9):
        y = 95 + (i - 1) * 62
        nodes.append({"name": f"h{i}", "x": 790, "y": y, "type": "host"})

    links = [["a1", "s1"], ["s1", "gw"], ["gw", "s2"]]
    links.extend([["s2", f"h{i}"] for i in range(1, 9)])
    return "Simulation V1 Traffic", hosts, nodes, links


def build_html(title, nodes, links):
    topology = json.dumps({"nodes": nodes, "links": links})
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, system-ui, sans-serif; background: #111317; color: #eef2f6; }}
    body {{ margin: 0; min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }}
    header {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-bottom: 1px solid #2b3038; background: #171a20; }}
    h1 {{ margin: 0; font-size: 16px; }}
    #stats {{ display: flex; gap: 16px; font-size: 13px; color: #bac4d0; }}
    main {{ display: grid; grid-template-columns: minmax(560px, 1fr) 340px; min-height: 0; }}
    #stage {{ overflow: hidden; background: #111317; }}
    svg {{ width: 100%; height: 100%; display: block; }}
    .link {{ stroke: #38414d; stroke-width: 2; }}
    .host {{ fill: #1d232c; stroke: #6a7481; stroke-width: 2; }}
    .attacker {{ fill: #3a1f26; stroke: #ff6b7a; stroke-width: 2; }}
    .gateway {{ fill: #263824; stroke: #72e28b; stroke-width: 2; }}
    .switch {{ fill: #263241; stroke: #8ea1b5; stroke-width: 2; }}
    .label {{ fill: #eef2f6; font-size: 12px; text-anchor: middle; dominant-baseline: middle; pointer-events: none; }}
    .packet {{ stroke: white; stroke-width: 1.5; }}
    aside {{ border-left: 1px solid #2b3038; background: #171a20; min-height: 0; overflow: hidden; display: flex; flex-direction: column; }}
    aside h2 {{ margin: 0; padding: 12px 14px; font-size: 14px; border-bottom: 1px solid #2b3038; }}
    #events {{ overflow: auto; padding: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
    .event {{ padding: 7px 8px; border-bottom: 1px solid #242a32; color: #d7dee7; white-space: nowrap; }}
    .legend {{ display: flex; gap: 10px; padding: 8px 10px; border-bottom: 1px solid #242a32; font-size: 12px; }}
    .ICMP {{ fill: #55c2ff; color: #55c2ff; }}
    .TCP {{ fill: #ffcf5a; color: #ffcf5a; }}
    .UDP {{ fill: #72e28b; color: #72e28b; }}
    .IP {{ fill: #d08cff; color: #d08cff; }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div id="stats">
      <span>Packets: <strong id="count">0</strong></span>
      <span>Last: <strong id="last">waiting</strong></span>
      <span>Status: <strong id="status">loading</strong></span>
    </div>
  </header>
  <main>
    <section id="stage"><svg id="svg" viewBox="0 0 900 640"></svg></section>
    <aside>
      <h2>Live packets</h2>
      <div class="legend">
        <span class="UDP">UDP</span>
        <span class="TCP">TCP</span>
        <span class="ICMP">ICMP</span>
        <span class="IP">IP</span>
      </div>
      <div id="events"></div>
    </aside>
  </main>
  <script>
    const topology = {topology};
    const svg = document.getElementById("svg");
    const events = document.getElementById("events");
    const countEl = document.getElementById("count");
    const lastEl = document.getElementById("last");
    const statusEl = document.getElementById("status");
    const positions = {{}};
    let packetLayer = null;
    let attackDot = null;
    let attackTimer = null;
    let count = 0;
    let lastSeen = 0;

    function el(name, attrs = {{}}) {{
      const node = document.createElementNS("http://www.w3.org/2000/svg", name);
      for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
      return node;
    }}

    function drawTopology() {{
      for (const node of topology.nodes) positions[node.name] = node;
      for (const [a, b] of topology.links) {{
        svg.appendChild(el("line", {{ x1: positions[a].x, y1: positions[a].y, x2: positions[b].x, y2: positions[b].y, class: "link" }}));
      }}
      for (const node of topology.nodes) {{
        if (node.type === "switch" || node.type === "gateway") {{
          svg.appendChild(el("rect", {{ x: node.x - 42, y: node.y - 24, width: 84, height: 48, rx: 7, class: node.type }}));
        }} else {{
          svg.appendChild(el("circle", {{ cx: node.x, cy: node.y, r: 30, class: node.type }}));
        }}
        svg.appendChild(el("text", {{ x: node.x, y: node.y, class: "label" }})).textContent = node.name;
      }}
      packetLayer = el("g");
      svg.appendChild(packetLayer);
    }}

    function animatePacket(packet) {{
      if (packet.src_host === "a1" && packet.dst_label === "h1-h8") {{
        showAttackFlow(packet);
        return;
      }}

      const src = positions[packet.src_host];
      const dst = positions[packet.dst_host];
      if (!src || !dst) return;
      const packetCount = packet.count || 1;
      const radius = Math.min(26, 7 + Math.sqrt(packetCount) * 4);
      const dot = el("circle", {{ cx: src.x, cy: src.y, r: radius, class: `packet ${{packet.protocol}}` }});
      packetLayer.appendChild(dot);
      const path = buildPacketPath(packet.src_host, packet.dst_host);
      const started = performance.now();
      const duration = 1100;
      const cleanup = setTimeout(() => dot.remove(), duration + 250);
      function frame(now) {{
        if (!dot.isConnected) return;
        const progress = Math.min((now - started) / duration, 1);
        const visualProgress = 0.15 + progress * 0.7;
        const scaled = visualProgress * (path.length - 1);
        const index = Math.min(Math.floor(scaled), path.length - 2);
        const local = scaled - index;
        const a = positions[path[index]];
        const b = positions[path[index + 1]];
        dot.setAttribute("cx", a.x + (b.x - a.x) * local);
        dot.setAttribute("cy", a.y + (b.y - a.y) * local);
        dot.setAttribute("opacity", String(1 - progress * 0.85));
        if (progress < 1) requestAnimationFrame(frame);
        else {{
          clearTimeout(cleanup);
          dot.remove();
        }}
      }}
      requestAnimationFrame(frame);
    }}

    function showAttackFlow(packet) {{
      const packetCount = packet.count || 1;
      const radius = Math.min(34, 14 + Math.sqrt(packetCount) * 3);
      const x = (positions.gw.x + positions.s2.x) / 2;
      const y = positions.gw.y;

      if (!attackDot) {{
        attackDot = el("circle", {{ cx: x, cy: y, r: radius, class: `packet ${{packet.protocol}}` }});
        packetLayer.appendChild(attackDot);
      }}

      attackDot.setAttribute("r", radius);
      attackDot.setAttribute("class", `packet ${{packet.protocol}}`);
      attackDot.setAttribute("opacity", "0.95");

      clearTimeout(attackTimer);
      attackTimer = setTimeout(() => {{
        if (attackDot) attackDot.remove();
        attackDot = null;
      }}, 1200);
    }}

    function buildPacketPath(src, dst) {{
      if (src.startsWith("h") && dst.startsWith("h")) return [src, "s2", dst];
      if (src === "a1" && dst.startsWith("h")) return [src, "s1", "gw", "s2", dst];
      if (src.startsWith("h") && dst === "a1") return [src, "s2", "gw", "s1", dst];
      if (src === "gw" && dst.startsWith("h")) return [src, "s2", dst];
      if (src === "gw" && dst === "a1") return [src, "s1", dst];
      if (dst === "gw" && src.startsWith("h")) return [src, "s2", dst];
      if (dst === "gw" && src === "a1") return [src, "s1", dst];
      return [src, dst];
    }}

    function addEvent(packet) {{
      const packetCount = packet.count || 1;
      count += packetCount;
      countEl.textContent = String(count);
      const dstLabel = packet.dst_label || packet.dst_host;
      lastEl.textContent = `${{packet.src_host}} -> ${{dstLabel}}`;

      const key = `${{packet.protocol}}|${{packet.src_host}}|${{dstLabel}}`;
      const firstLine = events.firstElementChild;
      if (firstLine && firstLine.dataset.key === key) {{
        const total = Number(firstLine.dataset.count) + packetCount;
        firstLine.dataset.count = String(total);
        firstLine.textContent = `${{packet.protocol.padEnd(4)}} ${{packet.src_host}} -> ${{dstLabel}} x${{total}}`;
        return;
      }}

      const line = document.createElement("div");
      line.className = `event ${{packet.protocol}}`;
      line.dataset.key = key;
      line.dataset.count = String(packetCount);
      line.textContent = `${{packet.protocol.padEnd(4)}} ${{packet.src_host}} -> ${{dstLabel}}${{packetCount > 1 ? " x" + packetCount : ""}}`;
      events.prepend(line);
      while (events.children.length > 80) events.lastChild.remove();
    }}

    function groupPackets(packets) {{
      const grouped = new Map();
      for (const packet of packets) {{
        const attackFlow = packet.src_host === "a1" && packet.dst_host.startsWith("h");
        const groupedPacket = attackFlow
          ? {{ ...packet, dst_host: "s2", dst_label: "h1-h8" }}
          : packet;
        const key = `${{groupedPacket.protocol}}|${{groupedPacket.src_host}}|${{groupedPacket.dst_label || groupedPacket.dst_host}}`;
        if (!grouped.has(key)) grouped.set(key, {{ ...groupedPacket, count: 0 }});
        grouped.get(key).count += 1;
      }}
      return Array.from(grouped.values());
    }}

    async function init() {{
      const response = await fetch("/state", {{ cache: "no-store" }});
      const state = await response.json();
      lastSeen = state.latest_id;
      poll();
    }}

    async function poll() {{
      try {{
        const response = await fetch(`/packets?since=${{lastSeen}}`, {{ cache: "no-store" }});
        const packets = await response.json();
        statusEl.textContent = "connected";
        for (const packet of packets) {{
          lastSeen = Math.max(lastSeen, packet.id);
        }}
        for (const packet of groupPackets(packets)) {{
          addEvent(packet);
          animatePacket(packet);
        }}
      }} catch (error) {{
        statusEl.textContent = "connection lost";
      }} finally {{
        setTimeout(poll, 250);
      }}
    }}

    drawTopology();
    init();
  </script>
</body>
</html>
"""


def parse_tcpdump_line(line):
    ips = re.findall(r"10\.0\.[01]\.\d+", line)
    if len(ips) < 2:
        return None

    src_ip, dst_ip = ips[0], ips[1]
    src_host = HOSTS.get(src_ip)
    dst_host = HOSTS.get(dst_ip)
    if not src_host or not dst_host or src_host == dst_host:
        return None

    if "ICMP" in line:
        protocol = "ICMP"
    elif re.search(r": UDP,| UDP,", line):
        protocol = "UDP"
    elif "Flags" in line:
        protocol = "TCP"
    elif re.search(r"\.\d+ > .*\.\d+:", line):
        protocol = "UDP"
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


def is_duplicate_packet(packet):
    now = time.time()
    key = (packet["src_ip"], packet["dst_ip"], packet["protocol"])

    for old_key, old_time in list(DEDUP_CACHE.items()):
        if now - old_time > 0.15:
            del DEDUP_CACHE[old_key]

    if key in DEDUP_CACHE:
        return True

    DEDUP_CACHE[key] = now
    return False


def run_tcpdump(interface):
    global TCPDUMP_PROCESS, CURRENT_PACKET_ID
    command = ["tcpdump", "-l", "-nn", "-i", interface, "net", "10.0.0.0/23"]
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
        if packet and not is_duplicate_packet(packet):
            CURRENT_PACKET_ID += 1
            packet["id"] = CURRENT_PACKET_ID
            print(f"{packet['protocol']} {packet['src_host']} -> {packet['dst_host']}", flush=True)
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

        if self.path.startswith("/packets"):
            since = 0
            if "?" in self.path:
                for part in self.path.split("?", 1)[1].split("&"):
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

        if self.path == "/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps({"latest_id": CURRENT_PACKET_ID}).encode())
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    global DEBUG, HOSTS, HTML
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation", choices=["v0.1", "v1"], default="v1")
    parser.add_argument("--interface", default="any")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    DEBUG = args.debug

    if args.simulation == "v0.1":
        title, HOSTS, nodes, links = build_v0_1_topology()
    else:
        title, HOSTS, nodes, links = build_v1_topology()

    HTML = build_html(title, nodes, links)
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
