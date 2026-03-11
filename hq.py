#!/usr/bin/env python3
"""
🔥 FIRETEAM HQ — Live Command Center

Unified HTTP server + Pro Mode daemon + live dashboard.
Serves a web UI at http://localhost:4040 that shows agent
status in real-time and lets you fire/pause/monitor agents.

Usage:
    python3 hq.py                   # Start HQ (daemon + dashboard)
    python3 hq.py --port 5050       # Custom port
    python3 hq.py --no-auto         # Dashboard only, no auto-fire
    python3 hq.py --generate        # Generate static dashboard.html

Requirements: Python 3.6+, `claude` CLI on PATH (for Pro Mode)
"""

import subprocess, threading, time, json, re, os, sys, signal
import hashlib, argparse, traceback
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

# ═══════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════

DEFAULT_PORT = 4040
DEFAULT_POLL = 30
MAX_PARALLEL = 4
CLAUDE_CMD = "claude"
CLAUDE_ARGS = ["-p"]

# ═══════════════════════════════════════════════════
# FIND .fireteam/
# ═══════════════════════════════════════════════════

def find_ft():
    d = Path.cwd()
    while d != d.parent:
        if (d / ".fireteam").is_dir(): return d / ".fireteam", d
        d = d.parent
    print("Error: .fireteam/ not found.", file=sys.stderr); sys.exit(1)

FT, ROOT = find_ft()
LOG_DIR = FT / "logs"
LOG_DIR.mkdir(exist_ok=True)

def rf(p):
    try: return Path(p).read_text(encoding="utf-8")
    except: return ""

def ex(pat, txt, d=""):
    m = re.search(pat, txt); return m.group(1).strip() if m else d

# ═══════════════════════════════════════════════════
# PARSERS
# ═══════════════════════════════════════════════════

def parse_agents():
    c = rf(FT/"ROSTER.md"); agents = []
    for b in re.split(r"^### ", c, flags=re.MULTILINE)[1:]:
        ls = b.strip().split("\n"); nm = ls[0].strip()
        aid=""; pl=""; rsp=[]; ir=False
        for l in ls[1:]:
            m=re.match(r".*\*\*Callsign:\*\*\s*`([^`]+)`",l)
            if m: aid=m.group(1)
            m=re.match(r".*\*\*Platform:\*\*\s*(.*)",l)
            if m: pl=m.group(1).strip().strip("<!--").strip("-->").strip()
            if "Duties" in l or "Responsibilities" in l: ir=True; continue
            if ir and l.strip().startswith("- "): rsp.append(l.strip().lstrip("- "))
            elif ir and not l.strip().startswith("- ") and l.strip(): ir=False
        if aid: agents.append({"name":nm,"id":aid,"platform":pl,"responsibilities":rsp})
    return agents

def parse_tasks():
    tasks={}; td=FT/"tasks"
    if not td.is_dir(): return tasks
    for f in sorted(td.glob("OBJ-*.md")):
        c=rf(f); t={"id":f.stem,"path":str(f)}
        t["status"]=ex(r"\*\*Status:\*\*\s*(\S+)",c,"backlog")
        t["checked_out"]=ex(r"\*\*Checked out by:\*\*\s*(\S+)",c,"")
        t["priority"]=ex(r"\*\*Priority:\*\*\s*(\S+)",c,"P2")
        t["title"]=ex(r"#\s*OBJ-\d+:\s*(.*)",c,f.stem)
        dep_raw=ex(r"## Depends On\s*\n\s*(.*?)(?=\n##|\Z)",c,"none")
        t["depends"]=[m.group(0) for m in re.finditer(r"OBJ-\d+",dep_raw)] if dep_raw.lower()!="none" else []
        t["assignee"]=t["checked_out"] or extract_board_assignee(t["id"])
        ch=re.findall(r"- \[([ xX])\]",c)
        t["criteria_total"]=len(ch); t["criteria_done"]=sum(1 for x in ch if x.lower()=="x")
        # Goal chain
        gc=ex(r"\*\*Mission:\*\*\s*(.*)",c,"")
        t["goal_mission"]=gc
        t["goal_goal"]=ex(r"\*\*Goal:\*\*\s*(.*)",c,"")
        tasks[f.stem]=t
    return tasks

def extract_board_assignee(oid):
    c=rf(FT/"BOARD.md")
    for l in c.split("\n"):
        if oid in l and "|" in l:
            cells=[x.strip() for x in l.split("|")[1:-1]]
            if len(cells)>=3 and cells[2]: return cells[2]
    return ""

def parse_checkpoints():
    ckpts={}; cd=FT/"checkpoints"
    if not cd.is_dir(): return ckpts
    for f in cd.glob("*.md"):
        if f.stem.endswith(("-soul","-heartbeat")) or f.name==".gitkeep": continue
        c=rf(f); ck={"agent":f.stem}
        for k,p in[("updated",r"\*\*Last updated:\*\*\s*(.*)"),("task",r"\*\*Objective:\*\*\s*(.*)"),("progress",r"\*\*Completion:\*\*\s*(.*)"),("focus",r"\*\*Current focus:\*\*\s*(.*)")]:
            m=re.search(p,c); ck[k]=m.group(1).strip() if m else ""
        ck["mtime"]=datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        ckpts[f.stem]=ck
    return ckpts

def parse_daily_logs():
    md=FT/"memory"; logs=[]
    if not md.is_dir(): return logs
    for f in sorted(md.glob("*.md"),reverse=True)[:3]:
        if f.name==".gitkeep": continue
        c=rf(f); ss=[]
        for b in re.split(r"^## Session:",c,flags=re.MULTILINE)[1:]:
            ls=b.strip().split("\n"); ss.append({"header":"Session: "+ls[0].strip(),"content":b.strip()[:300]})
        logs.append({"date":f.stem,"sessions":ss})
    return logs

def parse_handoffs():
    hd=FT/"handoffs"; hs=[]
    if not hd.is_dir(): return hs
    for f in sorted(hd.glob("HO-*.md")):
        c=rf(f); t=ex(r"#\s*HO-\d+:\s*(.*)",c,f.stem)
        st=ex(r"\*\*Status:\*\*\s*(\S+)",c,"pending")
        hs.append({"id":f.stem,"title":t,"status":st})
    return hs

def parse_project():
    c=rf(FT/"MISSION.md")
    ov=ex(r"## Mission\s*\n(.*?)(?=\n##|\Z)",c,"").strip()
    st=ex(r"\*\*Status:\*\*\s*(\S+)",c,"Planning")
    return{"overview":ov,"status":st}

def load_pro_config():
    cfg_path=FT/"pro.yml"
    if not cfg_path.exists(): return {}
    content=rf(cfg_path); config={}; cur=None
    for line in content.split("\n"):
        line=line.rstrip()
        if not line or line.startswith("#"): continue
        if not line.startswith(" ") and line.endswith(":"):
            cur=line[:-1].strip(); config[cur]={"cli":CLAUDE_CMD,"model":"","args":""}
        elif cur and ":" in line:
            k,v=line.split(":",1); config[cur][k.strip()]=v.strip()
    return config

def full_state(orchestrator):
    """Build complete state for the dashboard."""
    tasks=parse_tasks()
    mission_content = rf(FT/"MISSION.md")
    has_mission = bool(re.search(r"## Mission\s*\n\s*\S", mission_content))
    has_tasks = len(tasks) > 0
    return {
        "time":datetime.now().strftime("%H:%M:%S"),
        "generated":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project":parse_project(),
        "agents":parse_agents(),
        "tasks":tasks,
        "checkpoints":parse_checkpoints(),
        "daily_logs":parse_daily_logs(),
        "handoffs":parse_handoffs(),
        "pro_config":load_pro_config(),
        "ready": has_mission and has_tasks,
        "launching": getattr(orchestrator, '_bootstrapping', False) if orchestrator else False,
        "daemon":{
            "running":orchestrator.active if orchestrator else False,
            "auto_fire":orchestrator.auto_fire if orchestrator else False,
            "poll_interval":orchestrator.interval if orchestrator else DEFAULT_POLL,
            "max_parallel":orchestrator.max_parallel if orchestrator else MAX_PARALLEL,
            "running_tasks":list(orchestrator.running.keys()) if orchestrator else [],
            "completed":list(orchestrator.completed) if orchestrator else [],
            "failed":list(orchestrator.failed) if orchestrator else [],
            "active_count":orchestrator.active_count if orchestrator else 0,
        },
        "logs":list_logs(),
    }

def list_logs():
    logs=[]
    if LOG_DIR.is_dir():
        for f in sorted(LOG_DIR.glob("*.log"),reverse=True)[:20]:
            logs.append({"name":f.name,"size":f.stat().st_size,"mtime":datetime.fromtimestamp(f.stat().st_mtime).strftime("%H:%M:%S")})
    return logs

# ═══════════════════════════════════════════════════
# ORCHESTRATOR (Pro Mode Engine)
# ═══════════════════════════════════════════════════

class Orchestrator:
    def __init__(self, auto_fire=True, interval=DEFAULT_POLL, max_parallel=MAX_PARALLEL):
        self.auto_fire = auto_fire
        self.interval = interval
        self.max_parallel = max_parallel
        self.active = False
        self.running = {}
        self.completed = set()
        self.failed = set()
        self.lock = threading.Lock()
        self.pro_config = load_pro_config()
        self._thread = None
        self._stop = threading.Event()
        self.event_log = []  # recent events for the UI
        self._bootstrapping = False

    def log_event(self, level, msg):
        entry = {"time":datetime.now().strftime("%H:%M:%S"),"level":level,"msg":msg}
        self.event_log.append(entry)
        if len(self.event_log) > 50: self.event_log = self.event_log[-50:]
        colors={"info":"\033[32m","fire":"\033[36m","done":"\033[32m","warn":"\033[33m","error":"\033[31m"}
        c=colors.get(level,"\033[0m")
        print(f"{c}[{entry['time']}] {msg}\033[0m")

    def start(self):
        if self.active: return
        self.active = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.log_event("info", "Daemon started")

    def stop(self):
        self.active = False
        self._stop.set()
        self.log_event("info", "Daemon stopped")

    @property
    def active_count(self):
        with self.lock: return len(self.running)

    def _loop(self):
        last_hash = ""
        while not self._stop.is_set():
            h = self._board_hash()
            if h != last_hash:
                if self.auto_fire:
                    self._run_pass()
                last_hash = h
            self._stop.wait(self.interval)

    def _board_hash(self):
        h=hashlib.md5(); h.update(rf(FT/"BOARD.md").encode())
        td=FT/"tasks"
        if td.is_dir():
            for f in sorted(td.glob("OBJ-*.md")): h.update(rf(f).encode())
        return h.hexdigest()

    def _run_pass(self):
        tasks=parse_tasks()
        deps={tid:set(t["depends"]) for tid,t in tasks.items()}
        done_ids={tid for tid,t in tasks.items() if t["status"] in("done","review")} | self.completed
        ext_running={tid for tid,t in tasks.items() if t["status"]=="in-progress" and tid not in self.running}
        ready=[]
        for tid,t in tasks.items():
            if t["status"]!="backlog": continue
            if tid in self.running or tid in done_ids: continue
            if set(t["depends"])<=done_ids: ready.append(t)
        ready.sort(key=lambda t:{"P0":0,"P1":1,"P2":2}.get(t["priority"],3))
        for task in ready:
            if self.active_count>=self.max_parallel: break
            cs=task["assignee"]
            if not cs or cs in("<!--",""): continue
            self.fire_task(task["id"],cs)

    def fire_task(self, task_id, callsign=None):
        """Fire a specific task. Called by daemon or manually via API."""
        tasks=parse_tasks()
        task=tasks.get(task_id)
        if not task: self.log_event("error",f"Task {task_id} not found"); return False
        if task_id in self.running: self.log_event("warn",f"{task_id} already running"); return False
        if not callsign: callsign=task["assignee"]
        if not callsign: self.log_event("error",f"{task_id} has no assignee"); return False

        self.log_event("fire",f"DEPLOYING {callsign} → {task_id}: {task['title']}")
        self._checkout(task, callsign)
        prompt = self._assemble_prompt(task, callsign)
        cfg = self.pro_config.get(callsign, {})
        cli = cfg.get("cli", CLAUDE_CMD)
        model = cfg.get("model", "")

        cmd = [cli]
        if model: cmd.extend(["--model", model])
        cmd.extend(CLAUDE_ARGS)
        cmd.append(prompt)

        def run():
            lf = LOG_DIR/f"{task_id}_{callsign}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            try:
                result=subprocess.run(cmd,cwd=str(ROOT),capture_output=True,text=True,timeout=1800)
                lf.write_text(f"# {callsign} → {task_id}\n# Exit: {result.returncode}\n\n## STDOUT\n{result.stdout}\n\n## STDERR\n{result.stderr}\n",encoding="utf-8")
                if result.returncode==0:
                    self.log_event("done",f"{callsign} completed {task_id}")
                    with self.lock: self.completed.add(task_id); self.running.pop(task_id,None)
                else:
                    self.log_event("error",f"{callsign} failed {task_id} (exit {result.returncode})")
                    with self.lock: self.failed.add(task_id); self.running.pop(task_id,None)
            except subprocess.TimeoutExpired:
                self.log_event("warn",f"{callsign} timed out on {task_id}")
                with self.lock: self.failed.add(task_id); self.running.pop(task_id,None)
            except Exception as e:
                self.log_event("error",f"{callsign}: {e}")
                with self.lock: self.failed.add(task_id); self.running.pop(task_id,None)

        t=threading.Thread(target=run,daemon=True)
        t.start()
        with self.lock: self.running[task_id]={"thread":t,"callsign":callsign,"started":datetime.now().strftime("%H:%M:%S")}
        return True

    def launch_mission(self, prd_text, model="opus"):
        """Bootstrap the entire fireteam from a PRD. Fires team-lead with START_MISSION prompt."""
        if self._bootstrapping:
            self.log_event("warn", "Bootstrap already in progress")
            return False

        self._bootstrapping = True
        self.log_event("fire", "MISSION LAUNCH — bootstrapping team-lead with PRD")

        # Save PRD
        prd_path = FT / "PRD.md"
        prd_path.write_text(prd_text, encoding="utf-8")
        self.log_event("info", f"PRD saved to {prd_path}")

        # Read START_MISSION.md to get the prompt template
        start_prompt_path = ROOT / "START_MISSION.md"
        start_prompt = ""
        if start_prompt_path.exists():
            raw = rf(start_prompt_path)
            # Extract the prompt between the first ``` and closing ```
            m = re.search(r"## The Prompt\s*\n```\s*\n(.*?)```", raw, re.DOTALL)
            if m:
                start_prompt = m.group(1).strip()

        if not start_prompt:
            # Fallback inline prompt
            start_prompt = """You are the TEAM LEAD for this mission. You are the first operator deployed.
I've attached a PRD below. Bootstrap the Fireteam:
1. Fill in .fireteam/MISSION.md from the PRD
2. Create ROSTER.md with proposed operators
3. Create SOUL files for each operator in .fireteam/checkpoints/
4. Create HEARTBEAT files for each operator
5. Create task files in .fireteam/tasks/ with goal chains
6. Populate .fireteam/BOARD.md
7. Seed .fireteam/INTEL.md with key facts
8. Write today's field log
9. Write your checkpoint
Follow .fireteam/CONVENTIONS.md strictly. Every task needs a goal chain and acceptance criteria."""

        # Assemble full prompt
        full_prompt = f"""{start_prompt}

---

# THE PRD

{prd_text}

---

IMPORTANT: The .fireteam/ folder already exists with templates in .fireteam/templates/.
Use these templates when creating task files, soul files, heartbeat files, etc.
Work in the project directory: {ROOT}
"""

        # Get CLI config
        cfg = self.pro_config.get("team-lead", {})
        cli = cfg.get("cli", CLAUDE_CMD)
        use_model = cfg.get("model", model)

        cmd = [cli]
        if use_model:
            cmd.extend(["--model", use_model])
        cmd.extend(CLAUDE_ARGS)
        cmd.append(full_prompt)

        def run_bootstrap():
            lf = LOG_DIR / f"BOOTSTRAP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            try:
                self.log_event("info", f"Spawning team-lead ({cli} {use_model})...")
                result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=3600)
                lf.write_text(
                    f"# MISSION BOOTSTRAP\n# Exit: {result.returncode}\n\n## STDOUT\n{result.stdout}\n\n## STDERR\n{result.stderr}\n",
                    encoding="utf-8"
                )
                if result.returncode == 0:
                    self.log_event("done", "MISSION BOOTSTRAPPED — team-lead completed setup")
                    # Reload config in case team-lead updated pro.yml
                    self.pro_config = load_pro_config()
                else:
                    self.log_event("error", f"Bootstrap failed (exit {result.returncode}). Check logs.")
            except subprocess.TimeoutExpired:
                self.log_event("error", "Bootstrap timed out (60m limit)")
            except Exception as e:
                self.log_event("error", f"Bootstrap error: {e}")
            finally:
                self._bootstrapping = False

        t = threading.Thread(target=run_bootstrap, daemon=True)
        t.start()
        return True

    def _checkout(self, task, callsign):
        p=Path(task["path"]); c=rf(p); now=datetime.now().strftime("%Y-%m-%d %H:%M")
        c=re.sub(r"(\*\*Status:\*\*)\s*\S+",r"\1 in-progress",c)
        c=re.sub(r"(\*\*Checked out by:\*\*)\s*.*",f"\\1 {callsign}",c)
        c=re.sub(r"(\*\*Checkout time:\*\*)\s*.*",f"\\1 {now}",c)
        p.write_text(c,encoding="utf-8")

    def _assemble_prompt(self, task, callsign):
        parts=[]
        sp=FT/"checkpoints"/f"{callsign}-soul.md"
        if sp.exists(): parts.append(f"# YOUR IDENTITY\n{rf(sp)}")
        m=rf(FT/"MISSION.md")
        if m: parts.append(f"# MISSION\n{m}")
        intel=rf(FT/"INTEL.md")
        if intel: parts.append(f"# INTEL\n{intel}")
        today=datetime.now().strftime("%Y-%m-%d")
        lp=FT/"memory"/f"{today}.md"
        if lp.exists(): parts.append(f"# FIELD LOG\n{rf(lp)}")
        cp=FT/"checkpoints"/f"{callsign}.md"
        if cp.exists(): parts.append(f"# CHECKPOINT\n{rf(cp)}")
        hd=FT/"handoffs"
        if hd.is_dir():
            for hf in hd.glob("HO-*.md"):
                hc=rf(hf)
                if callsign in hc.lower(): parts.append(f"# HANDOFF: {hf.stem}\n{hc}")
        tc=rf(Path(task["path"]))
        parts.append(f"# OBJECTIVE: {task['id']}\n{tc}")
        parts.append(f"""# INSTRUCTIONS
You are operator `{callsign}`. Execute the objective above.
Work in: {ROOT}
When done:
1. Update task status to "review" in the task file
2. Update .fireteam/BOARD.md
3. Write checkpoint to .fireteam/checkpoints/{callsign}.md
4. Append to field log: .fireteam/memory/{today}.md
5. Create handoffs in .fireteam/handoffs/ if needed
6. If stuck, create a thread in .fireteam/comms/ and set status to "blocked"
""")
        return "\n\n---\n\n".join(parts)

# ═══════════════════════════════════════════════════
# HTTP SERVER
# ═══════════════════════════════════════════════════

orchestrator = None

class HQHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass  # suppress default logging

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.end_headers()
        self.wfile.write(json.dumps(data,default=str).encode())

    def _html(self, html):
        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/": self._html(DASHBOARD_HTML)
        elif path=="/api/state": self._json(full_state(orchestrator))
        elif path=="/api/events": self._json(orchestrator.event_log if orchestrator else [])
        elif path.startswith("/api/log/"):
            name=path.split("/api/log/")[1]
            lp=LOG_DIR/name
            if lp.exists() and lp.suffix==".log":
                self._json({"name":name,"content":rf(lp)[:50000]})
            else: self._json({"error":"not found"},404)
        else: self._json({"error":"not found"},404)

    def do_POST(self):
        path=urlparse(self.path).path
        ln=int(self.headers.get("Content-Length",0))
        body=json.loads(self.rfile.read(ln)) if ln>0 else {}

        if path=="/api/fire":
            tid=body.get("task_id","")
            cs=body.get("callsign","")
            if orchestrator and tid:
                ok=orchestrator.fire_task(tid,cs or None)
                self._json({"ok":ok})
            else: self._json({"error":"missing task_id"},400)

        elif path=="/api/daemon/start":
            if orchestrator:
                orchestrator.auto_fire=True
                orchestrator.start()
                self._json({"ok":True})

        elif path=="/api/daemon/stop":
            if orchestrator:
                orchestrator.auto_fire=False
                orchestrator.stop()
                self._json({"ok":True})

        elif path=="/api/daemon/config":
            if orchestrator:
                if "interval" in body: orchestrator.interval=int(body["interval"])
                if "max_parallel" in body: orchestrator.max_parallel=int(body["max_parallel"])
                if "auto_fire" in body: orchestrator.auto_fire=bool(body["auto_fire"])
                self._json({"ok":True})

        elif path=="/api/launch":
            prd = body.get("prd","")
            model = body.get("model","opus")
            auto = body.get("auto_fire", True)
            if not prd.strip():
                self._json({"error":"PRD is empty"},400)
            elif orchestrator:
                ok = orchestrator.launch_mission(prd, model)
                if ok and auto:
                    orchestrator.auto_fire = True
                    if not orchestrator.active:
                        orchestrator.start()
                self._json({"ok":ok})
            else:
                self._json({"error":"orchestrator not ready"},500)
        else:
            self._json({"error":"not found"},404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()

# ═══════════════════════════════════════════════════
# DASHBOARD HTML
# ═══════════════════════════════════════════════════

DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>FIRETEAM HQ</title>
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a12;--pan:#0e0e18;--bdr:#1a2a1a;--txt:#88aa88;--dim:#3a5a3a;
--grn:#33dd66;--red:#ee3344;--amb:#ddaa22;--blu:#4488ee;--pur:#aa55dd;--cyn:#33ccdd}
body{background:var(--bg);color:var(--txt);font-family:'Press Start 2P',monospace;font-size:8px;overflow-x:hidden}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--bdr);border-radius:3px}

/* HEADER */
.hdr{display:flex;justify-content:space-between;align-items:center;padding:10px 16px;background:var(--pan);border-bottom:3px solid var(--bdr)}
.hdr h1{font-size:10px;color:var(--grn);text-shadow:0 0 10px rgba(51,221,102,0.5)}
.hdr-r{display:flex;align-items:center;gap:12px}
.pill{font-size:7px;padding:3px 8px;border:2px solid;cursor:default}
.pill.on{color:var(--grn);border-color:var(--grn);text-shadow:0 0 6px rgba(51,221,102,0.5)}
.pill.off{color:var(--red);border-color:var(--red)}
.pill.plan{color:var(--amb);border-color:var(--amb)}
.htime{font-size:6px;color:var(--dim)}

/* CONTROLS BAR */
.ctrl{display:flex;gap:8px;padding:10px 16px;background:rgba(14,14,24,0.8);border-bottom:2px solid var(--bdr);align-items:center;flex-wrap:wrap}
.btn{font-family:'Press Start 2P',monospace;font-size:7px;padding:6px 12px;border:2px solid var(--bdr);background:var(--pan);color:var(--txt);cursor:pointer;transition:all 0.15s}
.btn:hover{border-color:var(--grn);color:var(--grn)}
.btn.fire{border-color:var(--grn);color:var(--grn)}
.btn.fire:hover{background:rgba(51,221,102,0.1)}
.btn.stop{border-color:var(--red);color:var(--red)}
.btn.stop:hover{background:rgba(238,51,68,0.1)}
.btn.active{background:rgba(51,221,102,0.15);border-color:var(--grn);color:var(--grn);text-shadow:0 0 6px rgba(51,221,102,0.3)}
.ctrl-sep{width:1px;height:20px;background:var(--bdr)}
.ctrl-label{color:var(--dim);font-size:6px}
.ctrl-val{color:var(--cyn);font-size:7px;margin-left:4px}

/* STATS */
.stats{display:flex;gap:6px;padding:8px 16px;flex-wrap:wrap}
.sg{flex:1;min-width:70px;background:var(--pan);border:2px solid var(--bdr);padding:8px}
.sgv{font-size:14px;line-height:1}.sgl{font-size:6px;color:var(--dim);margin-top:3px;text-transform:uppercase}

/* MAIN LAYOUT */
.main{display:grid;grid-template-columns:1fr 340px;gap:0;min-height:calc(100vh - 200px)}

/* TASK BOARD */
.board{padding:12px 16px;border-right:2px solid var(--bdr);overflow-y:auto}
.board-title{font-size:8px;color:var(--grn);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--bdr)}
.task{display:flex;align-items:center;gap:6px;padding:7px 8px;margin-bottom:4px;background:rgba(0,0,0,0.3);border:2px solid var(--bdr);border-radius:2px;transition:border-color 0.2s;cursor:pointer}
.task:hover{border-color:var(--grn)}
.task.running{border-color:var(--cyn);background:rgba(51,204,221,0.05);animation:taskPulse 2s infinite}
@keyframes taskPulse{0%,100%{border-color:var(--cyn)}50%{border-color:rgba(51,204,221,0.3)}}
.task.done{opacity:0.4;border-color:var(--bdr)}
.task.blocked{border-color:var(--red)}
.task.failed{border-color:var(--red);background:rgba(238,51,68,0.05)}
.t-id{color:var(--blu);min-width:52px}.t-title{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.t-pri{padding:2px 5px;border:1px solid;font-size:6px}
.t-pri.P0{color:var(--red);border-color:var(--red)}.t-pri.P1{color:var(--amb);border-color:var(--amb)}.t-pri.P2{color:var(--dim);border-color:var(--dim)}
.t-who{color:var(--dim);min-width:60px;text-align:right;font-size:6px}
.t-bar{width:28px;height:4px;background:#111;border-radius:1px;overflow:hidden}.t-bf{height:100%;background:var(--grn);border-radius:1px}
.t-fire{font-size:6px;padding:3px 6px;border:1px solid var(--grn);color:var(--grn);background:transparent;cursor:pointer;font-family:'Press Start 2P',monospace;opacity:0;transition:opacity 0.15s}
.task:hover .t-fire{opacity:1}
.t-fire:hover{background:rgba(51,221,102,0.15)}
.t-status{font-size:6px;padding:2px 5px;border:1px solid;border-radius:2px;min-width:52px;text-align:center}
.t-status.backlog{color:var(--dim);border-color:var(--dim)}
.t-status.in-progress{color:var(--cyn);border-color:var(--cyn)}
.t-status.blocked{color:var(--red);border-color:var(--red)}
.t-status.review{color:var(--amb);border-color:var(--amb)}
.t-status.done{color:var(--grn);border-color:var(--grn)}

/* DEP ARROWS */
.dep-tag{font-size:5px;color:var(--pur);margin-left:4px}

/* SIDE PANEL */
.side{display:flex;flex-direction:column;overflow:hidden}
.side-tab{display:flex;border-bottom:2px solid var(--bdr)}
.tab-btn{flex:1;padding:8px;text-align:center;font-size:7px;color:var(--dim);background:var(--pan);border:none;cursor:pointer;font-family:'Press Start 2P',monospace;border-bottom:2px solid transparent}
.tab-btn.on{color:var(--grn);border-bottom-color:var(--grn);text-shadow:0 0 4px rgba(51,221,102,0.3)}
.tab-pane{flex:1;overflow-y:auto;padding:10px 12px;display:none}
.tab-pane.on{display:block}

/* EVENTS LOG */
.evt{padding:4px 6px;margin-bottom:3px;border-left:2px solid var(--dim);font-size:6px;line-height:1.6}
.evt.fire{border-color:var(--cyn);color:var(--cyn)}.evt.done{border-color:var(--grn)}.evt.error{border-color:var(--red);color:var(--red)}.evt.warn{border-color:var(--amb);color:var(--amb)}
.evt-time{color:var(--dim);margin-right:6px}

/* AGENT DETAIL */
.ag-card{padding:8px;margin-bottom:6px;background:rgba(0,0,0,0.3);border:1px solid var(--bdr);border-radius:2px}
.ag-name{font-size:8px;margin-bottom:4px}.ag-meta{font-size:6px;color:var(--dim);line-height:1.7}

/* LOGS */
.log-item{padding:6px 8px;margin-bottom:4px;background:rgba(0,0,0,0.3);border:1px solid var(--bdr);cursor:pointer;font-size:6px;display:flex;justify-content:space-between}
.log-item:hover{border-color:var(--grn)}
.log-viewer{background:#000;padding:8px;font-size:6px;line-height:1.6;white-space:pre-wrap;word-break:break-all;max-height:400px;overflow-y:auto;border:1px solid var(--bdr);display:none}
.log-viewer.on{display:block}

.empty{text-align:center;padding:20px;color:var(--dim)}
.section-title{font-size:7px;color:var(--grn);margin:12px 0 8px;padding-bottom:4px;border-bottom:1px solid var(--bdr)}

/* LIVE INDICATOR */
.live{display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:6px}
.live.on{background:var(--grn);box-shadow:0 0 8px var(--grn);animation:livePulse 1.5s infinite}
.live.off{background:var(--red)}
@keyframes livePulse{0%,100%{opacity:1}50%{opacity:0.4}}

/* LAUNCH SCREEN */
.launch{position:fixed;inset:0;background:var(--bg);z-index:500;display:flex;align-items:center;justify-content:center;overflow-y:auto;padding:20px}
.launch.hidden{display:none}
.launch-card{width:100%;max-width:700px;background:var(--pan);border:3px solid var(--bdr);padding:28px 24px}
.launch-title{font-size:12px;color:var(--grn);text-align:center;margin-bottom:4px;text-shadow:0 0 10px rgba(51,221,102,0.5)}
.launch-sub{font-size:7px;color:var(--dim);text-align:center;margin-bottom:20px}
.launch-section{margin-bottom:14px}
.launch-label{font-size:7px;color:var(--grn);margin-bottom:6px;display:block}
.launch-textarea{
  width:100%;min-height:260px;background:#060610;border:2px solid var(--bdr);color:var(--txt);
  font-family:'Press Start 2P',monospace;font-size:7px;line-height:1.8;padding:12px;resize:vertical;
  outline:none;
}
.launch-textarea:focus{border-color:var(--grn)}
.launch-textarea::placeholder{color:var(--dim)}
.launch-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:16px}
.launch-select{
  font-family:'Press Start 2P',monospace;font-size:7px;padding:6px 10px;
  background:var(--pan);border:2px solid var(--bdr);color:var(--txt);
}
.launch-go{
  font-family:'Press Start 2P',monospace;font-size:9px;padding:10px 24px;
  background:rgba(51,221,102,0.1);border:3px solid var(--grn);color:var(--grn);
  cursor:pointer;text-shadow:0 0 8px rgba(51,221,102,0.4);flex:1;text-align:center;
  transition:all 0.2s;
}
.launch-go:hover{background:rgba(51,221,102,0.2);box-shadow:0 0 20px rgba(51,221,102,0.15)}
.launch-go:disabled{opacity:0.3;cursor:not-allowed}
.launch-opt{display:flex;gap:12px;align-items:center;margin-top:8px}
.launch-check{accent-color:var(--grn)}
.launch-check-label{font-size:6px;color:var(--dim);cursor:pointer}
.launch-template{font-size:6px;color:var(--cyn);cursor:pointer;text-decoration:underline;margin-left:auto}
.launch-template:hover{color:var(--grn)}

/* BOOTSTRAPPING OVERLAY */
.boot-overlay{position:fixed;inset:0;background:rgba(10,10,18,0.95);z-index:600;display:none;align-items:center;justify-content:center;flex-direction:column}
.boot-overlay.on{display:flex}
.boot-spinner{width:48px;height:48px;border:4px solid var(--bdr);border-top-color:var(--grn);border-radius:50%;animation:spin 1s linear infinite;margin-bottom:16px}
@keyframes spin{to{transform:rotate(360deg)}}
.boot-text{font-size:8px;color:var(--grn);text-shadow:0 0 10px rgba(51,221,102,0.4);text-align:center;margin-bottom:8px}
.boot-sub{font-size:6px;color:var(--dim);text-align:center;max-width:400px;line-height:1.8}
.boot-events{margin-top:16px;max-width:500px;width:100%;max-height:200px;overflow-y:auto;padding:0 16px}

@media(max-width:768px){.main{grid-template-columns:1fr}.side{max-height:50vh}}
</style>
</head>
<body>

<div class="launch" id="launchScreen">
  <div class="launch-card">
    <div class="launch-title">&#x1F525; FIRETEAM HQ</div>
    <div class="launch-sub">Paste your PRD below to deploy the squad</div>
    <div class="launch-section">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <label class="launch-label" style="margin:0">PRODUCT REQUIREMENTS</label>
        <span class="launch-template" onclick="loadTemplate()">LOAD TEMPLATE</span>
      </div>
      <textarea class="launch-textarea" id="prdInput" placeholder="# Project Name&#10;&#10;## Problem Statement&#10;What problem are we solving?&#10;&#10;## Solution Overview&#10;What are we building?&#10;&#10;## Core Features&#10;1. ...&#10;2. ...&#10;&#10;## Technical Preferences&#10;Frontend: ...&#10;Backend: ...&#10;&#10;## Constraints&#10;Timeline: ..."></textarea>
    </div>
    <div class="launch-row">
      <select class="launch-select" id="modelSelect">
        <option value="opus">OPUS (strategic)</option>
        <option value="sonnet" selected>SONNET (balanced)</option>
      </select>
      <button class="launch-go" id="launchBtn" onclick="launchMission()">&#x1F680; LAUNCH MISSION</button>
    </div>
    <div class="launch-opt">
      <input type="checkbox" id="autoFireCheck" class="launch-check" checked>
      <label for="autoFireCheck" class="launch-check-label">Auto-fire agents after bootstrap</label>
    </div>
  </div>
</div>

<div class="boot-overlay" id="bootOverlay">
  <div class="boot-spinner"></div>
  <div class="boot-text">DEPLOYING TEAM LEAD...</div>
  <div class="boot-sub">The team lead is reading your PRD, setting up the mission, creating tasks, and assembling the squad. This takes 2-5 minutes.</div>
  <div class="boot-events" id="bootEvents"></div>
</div>

<div id="dashboardWrap">
<div class="hdr">
  <div><h1>&#x1F525; FIRETEAM HQ</h1><div class="htime" id="projInfo"></div></div>
  <div class="hdr-r">
    <span class="pill" id="daemonPill">DAEMON OFF</span>
    <span class="pill" id="projPill"></span>
    <div class="htime" id="clock"></div>
  </div>
</div>

<div class="ctrl" id="controls">
  <button class="btn fire" onclick="startDaemon()">&#x25B6; START</button>
  <button class="btn stop" onclick="stopDaemon()">&#x25A0; STOP</button>
  <div class="ctrl-sep"></div>
  <span class="ctrl-label">ACTIVE:</span><span class="ctrl-val" id="activeCount">0</span>
  <span class="ctrl-label">DONE:</span><span class="ctrl-val" id="doneCount">0</span>
  <span class="ctrl-label">FAILED:</span><span class="ctrl-val" id="failCount" style="color:var(--red)">0</span>
  <div class="ctrl-sep"></div>
  <span class="ctrl-label">POLL:</span><span class="ctrl-val" id="pollVal">30s</span>
  <span class="ctrl-label">MAX:</span><span class="ctrl-val" id="maxVal">4</span>
</div>

<div class="stats" id="statsBar"></div>

<div class="main">
  <div class="board" id="taskBoard"></div>
  <div class="side">
    <div class="side-tab">
      <button class="tab-btn on" onclick="showTab('events')">COMMS</button>
      <button class="tab-btn" onclick="showTab('agents')">ROSTER</button>
      <button class="tab-btn" onclick="showTab('logs')">LOGS</button>
    </div>
    <div class="tab-pane on" id="tab-events"></div>
    <div class="tab-pane" id="tab-agents"></div>
    <div class="tab-pane" id="tab-logs"></div>
  </div>
</div>
</div><!-- /dashboardWrap -->

<script>
let S = null;
let events = [];

async function poll() {
  try {
    const r = await fetch('/api/state');
    S = await r.json();
    const er = await fetch('/api/events');
    events = await er.json();
    render();
  } catch(e) { console.error(e); }
}

function render() {
  if (!S) return;
  updateViewState();
  if (!S.ready && !S.launching) return;
  // Clock
  document.getElementById('clock').textContent = S.time;
  document.getElementById('projInfo').textContent = (S.project.overview || 'NO MISSION').substring(0,60).toUpperCase();
  const pp = document.getElementById('projPill');
  pp.textContent = S.project.status || 'PLANNING';
  pp.className = 'pill ' + (S.project.status === 'Active' ? 'on' : 'plan');

  // Daemon status
  const dp = document.getElementById('daemonPill');
  if (S.daemon.running && S.daemon.auto_fire) {
    dp.textContent = 'AUTO'; dp.className = 'pill on';
  } else if (S.daemon.running) {
    dp.textContent = 'MANUAL'; dp.className = 'pill plan';
  } else {
    dp.textContent = 'OFF'; dp.className = 'pill off';
  }

  // Counters
  document.getElementById('activeCount').textContent = S.daemon.active_count;
  document.getElementById('doneCount').textContent = S.daemon.completed.length;
  document.getElementById('failCount').textContent = S.daemon.failed.length;
  document.getElementById('pollVal').textContent = S.daemon.poll_interval + 's';
  document.getElementById('maxVal').textContent = S.daemon.max_parallel;

  // Stats
  const tasks = Object.values(S.tasks);
  const total = tasks.length;
  const done = tasks.filter(t => t.status === 'done').length;
  const ip = tasks.filter(t => t.status === 'in-progress').length;
  const blk = tasks.filter(t => t.status === 'blocked').length;
  document.getElementById('statsBar').innerHTML = [
    ['--blu',total,'OBJECTIVES'],['--grn',done,'COMPLETE'],['--cyn',ip,'DEPLOYED'],
    ['--red',blk,'STUCK'],['--pur',S.agents.length,'OPERATORS'],['--amb',S.handoffs.length,'HANDOFFS'],
  ].map(([c,v,l]) => `<div class="sg"><div class="sgv" style="color:var(${c})">${v}</div><div class="sgl">${l}</div></div>`).join('');

  renderBoard();
  renderEvents();
  renderAgents();
  renderLogs();
}

function renderBoard() {
  const tasks = Object.values(S.tasks);
  const running = new Set(S.daemon.running_tasks);
  const failed = new Set(S.daemon.failed);

  // Group by status
  const groups = {
    'in-progress': tasks.filter(t => t.status === 'in-progress'),
    'blocked': tasks.filter(t => t.status === 'blocked'),
    'backlog': tasks.filter(t => t.status === 'backlog'),
    'review': tasks.filter(t => t.status === 'review'),
    'done': tasks.filter(t => t.status === 'done'),
  };

  let html = '';
  for (const [status, items] of Object.entries(groups)) {
    if (items.length === 0) continue;
    const label = {'in-progress':'&#x1F7E2; DEPLOYED','blocked':'&#x1F534; BLOCKED','backlog':'&#x26AA; BACKLOG','review':'&#x1F7E1; IN REVIEW','done':'&#x2705; COMPLETE'}[status] || status;
    html += `<div class="section-title">${label} (${items.length})</div>`;
    for (const t of items) {
      const pct = t.criteria_total ? Math.round(t.criteria_done / t.criteria_total * 100) : 0;
      const isRunning = running.has(t.id);
      const isFailed = failed.has(t.id);
      let cls = 'task';
      if (isRunning) cls += ' running';
      if (t.status === 'done') cls += ' done';
      if (t.status === 'blocked') cls += ' blocked';
      if (isFailed) cls += ' failed';
      const deps = t.depends.length ? `<span class="dep-tag">← ${t.depends.join(', ')}</span>` : '';
      const fireBtn = t.status === 'backlog' ? `<button class="t-fire" onclick="event.stopPropagation();fireSingle('${t.id}','${t.assignee}')">FIRE</button>` : '';
      html += `<div class="${cls}">
        <span class="t-id">${esc(t.id)}</span>
        <span class="t-title">${esc(t.title)}${deps}</span>
        <span class="t-pri ${t.priority}">${t.priority}</span>
        <span class="t-who">${esc(t.assignee||'-')}</span>
        <span class="t-status ${t.status}">${isRunning?'RUNNING':t.status}</span>
        <div class="t-bar"><div class="t-bf" style="width:${pct}%"></div></div>
        ${fireBtn}
      </div>`;
    }
  }
  if (!tasks.length) html = '<div class="empty">NO OBJECTIVES</div>';
  document.getElementById('taskBoard').innerHTML = '<div class="board-title">&#x25B6; OBJECTIVES BOARD</div>' + html;
}

function renderEvents() {
  const el = document.getElementById('tab-events');
  if (!events.length) { el.innerHTML = '<div class="empty">COMMS QUIET</div>'; return; }
  el.innerHTML = events.slice().reverse().map(e =>
    `<div class="evt ${e.level}"><span class="evt-time">${e.time}</span>${esc(e.msg)}</div>`
  ).join('');
}

function renderAgents() {
  const el = document.getElementById('tab-agents');
  if (!S.agents.length) { el.innerHTML = '<div class="empty">NO ROSTER</div>'; return; }
  const running = S.daemon.running_tasks;
  const runMap = {};
  if (S.daemon.running_tasks) {
    // We don't have callsign→task mapping in state easily, derive from tasks
    for (const tid of running) {
      const t = S.tasks[tid];
      if (t) runMap[t.assignee] = tid;
    }
  }
  el.innerHTML = S.agents.map(a => {
    const ck = S.checkpoints[a.id] || {};
    const cfg = S.pro_config[a.id] || {};
    const isRunning = a.id in runMap;
    const statusDot = isRunning ? '<span class="live on"></span>' : '<span class="live off"></span>';
    return `<div class="ag-card">
      <div class="ag-name">${statusDot}${esc(a.name)} <span style="color:var(--dim)">[${esc(a.id)}]</span></div>
      <div class="ag-meta">
        Model: ${esc(cfg.model || 'default')}<br>
        ${isRunning ? 'Working on: '+runMap[a.id] : ck.focus ? 'Last: '+esc(ck.focus) : 'Idle'}<br>
        ${ck.progress ? 'Progress: '+esc(ck.progress) : ''}
      </div>
    </div>`;
  }).join('');
}

function renderLogs() {
  const el = document.getElementById('tab-logs');
  if (!S.logs.length) { el.innerHTML = '<div class="empty">NO LOGS</div>'; return; }
  el.innerHTML = S.logs.map(l =>
    `<div class="log-item" onclick="viewLog('${esc(l.name)}')">${esc(l.name)}<span style="color:var(--dim)">${l.mtime}</span></div>`
  ).join('') + '<div class="log-viewer" id="logViewer"></div>';
}

async function viewLog(name) {
  const r = await fetch('/api/log/' + name);
  const d = await r.json();
  const lv = document.getElementById('logViewer');
  if (lv) { lv.textContent = d.content || 'Empty'; lv.classList.add('on'); }
}

// ACTIONS
async function startDaemon() {
  await fetch('/api/daemon/start', {method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
}
async function stopDaemon() {
  await fetch('/api/daemon/stop', {method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
}
async function fireSingle(taskId, callsign) {
  await fetch('/api/fire', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({task_id:taskId,callsign:callsign||''})});
}

function showTab(id) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('on'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('on'));
  document.getElementById('tab-'+id).classList.add('on');
  event.target.classList.add('on');
}

function esc(s) { const d = document.createElement('div'); d.textContent = s||''; return d.innerHTML; }

// POLL LOOP
poll();
setInterval(poll, 3000);

// PRD TEMPLATE
const PRD_TEMPLATE = `# Product Requirements Document

## Project Name



## Problem Statement

<!-- 2-3 sentences. What problem, for whom? -->


## Solution Overview

<!-- 2-3 sentences. What are we building? -->


## Target Users

-

## Core Features (Priority Order)

| # | Feature | Priority | Notes |
|---|---------|----------|-------|
| 1 | | Must-Have | |
| 2 | | Must-Have | |
| 3 | | Should-Have | |
| 4 | | Nice-to-Have | |

## Technical Preferences

- Frontend:
- Backend:
- Database:
- Deployment:

## Design Direction



## Constraints

-

## Out of Scope

-

## Success Criteria

- [ ]
- [ ]
- [ ]
`;

function loadTemplate() {
  document.getElementById('prdInput').value = PRD_TEMPLATE;
}

async function launchMission() {
  const prd = document.getElementById('prdInput').value.trim();
  if (!prd) { alert('Paste your PRD first'); return; }

  const model = document.getElementById('modelSelect').value;
  const autoFire = document.getElementById('autoFireCheck').checked;
  const btn = document.getElementById('launchBtn');

  btn.disabled = true;
  btn.textContent = 'LAUNCHING...';

  try {
    const r = await fetch('/api/launch', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({prd, model, auto_fire: autoFire})
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById('launchScreen').classList.add('hidden');
      document.getElementById('bootOverlay').classList.add('on');
    } else {
      alert('Launch failed: ' + (d.error || 'unknown'));
      btn.disabled = false;
      btn.textContent = '\u{1F680} LAUNCH MISSION';
    }
  } catch(e) {
    alert('Error: ' + e.message);
    btn.disabled = false;
    btn.textContent = '\u{1F680} LAUNCH MISSION';
  }
}

function updateViewState() {
  if (!S) return;
  const launch = document.getElementById('launchScreen');
  const boot = document.getElementById('bootOverlay');
  const dash = document.getElementById('dashboardWrap');

  if (S.launching) {
    launch.classList.add('hidden');
    boot.classList.add('on');
    dash.style.display = 'none';
    // Show events in boot overlay
    const be = document.getElementById('bootEvents');
    be.innerHTML = events.slice(-8).map(e =>
      `<div class="evt ${e.level}"><span class="evt-time">${e.time}</span>${esc(e.msg)}</div>`
    ).join('');
  } else if (S.ready) {
    launch.classList.add('hidden');
    boot.classList.remove('on');
    dash.style.display = '';
  } else {
    // Only show launch if boot overlay isn't already showing
    if (!boot.classList.contains('on')) {
      launch.classList.remove('hidden');
    }
    dash.style.display = 'none';
  }
}
</script>
</body>
</html>'''

# ═══════════════════════════════════════════════════
# STATIC GENERATION (fallback)
# ═══════════════════════════════════════════════════

def generate_static(output):
    """Generate a static dashboard.html (no server needed)."""
    state = full_state(None)
    html = DASHBOARD_HTML.replace(
        "async function poll() {",
        f"let S = {json.dumps(state, default=str)};\nlet events = [];\nfunction render_static(){{render()}};\nsetTimeout(render_static,100);\nasync function poll_disabled() {{"
    )
    Path(output).write_text(html, encoding="utf-8")
    print(f"Static dashboard: {output}")

# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🔥 Fireteam HQ — Live Command Center")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--interval", type=int, default=DEFAULT_POLL)
    parser.add_argument("--max-parallel", type=int, default=MAX_PARALLEL)
    parser.add_argument("--no-auto", action="store_true", help="Start without auto-fire (manual control via UI)")
    parser.add_argument("--generate", action="store_true", help="Generate static dashboard.html and exit")
    args = parser.parse_args()

    if args.generate:
        generate_static(ROOT / "dashboard.html")
        return

    global orchestrator
    orchestrator = Orchestrator(
        auto_fire=not args.no_auto,
        interval=args.interval,
        max_parallel=args.max_parallel
    )

    if not args.no_auto:
        orchestrator.start()

    server = HTTPServer(("127.0.0.1", args.port), HQHandler)

    def shutdown(sig, frame):
        print("\nShutting down...")
        orchestrator.stop()
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print()
    print(f"\033[36m{'═'*50}\033[0m")
    print(f"\033[36m  🔥 FIRETEAM HQ — Live Command Center\033[0m")
    print(f"\033[36m{'═'*50}\033[0m")
    print(f"  Dashboard:  http://localhost:{args.port}")
    print(f"  Project:    {ROOT}")
    print(f"  Auto-fire:  {'ON' if not args.no_auto else 'OFF (manual via UI)'}")
    print(f"  Interval:   {args.interval}s")
    print(f"  Parallel:   {args.max_parallel} max")
    pro_cfg = load_pro_config()
    if pro_cfg:
        print(f"  Operators:  {len(pro_cfg)}")
        for cs, cfg in pro_cfg.items():
            print(f"              {cs} → {cfg.get('cli','claude')} ({cfg.get('model','default')})")
    print(f"\033[36m{'═'*50}\033[0m")
    print()

    threading.Thread(target=server.serve_forever, daemon=True).start()

    # Keep main thread alive for signal handling
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
