"""The cloned voice's server (~/navoiy-stack/work/tts_server.py, port 8765), started and stopped from the editor.

Started the way STATUS.md says: a shell writes its PID to tts_server.shellpid and execs the server, so that PID is
the server's. It is stopped only by that PID, and only if that process really is tts_server.py (never by a name
pattern). Before starting, the port is checked: if something already answers there, it is used as it is.
"""
import socket
import subprocess
import time
from pathlib import Path

STACK = Path.home() / "navoiy-stack"
PIDFILE = STACK / "work" / "tts_server.shellpid"
LOG = STACK / "work" / "tts_server.log"
PORT = 8765


def up(port=PORT):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def ours():
    """The PID in the PID file, if that process is alive and is the voice server."""
    try:
        pid = int(PIDFILE.read_text().strip())
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode()
    except (OSError, ValueError):
        return None
    return pid if "tts_server.py" in cmd else None


def status():
    return {"up": up(), "pid": ours(), "installed": (STACK / "work" / "tts_server.py").exists()}


def start(wait=300):
    """Start the server unless one already answers; wait until it does (the model takes about a minute to load)."""
    if up():
        return "already running"
    if not (STACK / "work" / "tts_server.py").exists():
        raise RuntimeError("the voice stack is not installed (~/navoiy-stack)")
    cmd = f"cd {STACK / 'CosyVoice'} && echo $$ > {PIDFILE} && exec .venv/bin/python ../work/tts_server.py {PORT}"
    with open(LOG, "ab") as log:
        subprocess.Popen(["bash", "-c", cmd], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < wait:
        if up():
            return "started"
        time.sleep(2)
    raise RuntimeError(f"the voice server did not come up in {wait} s (see {LOG})")


def stop():
    pid = ours()
    if pid is None:
        return "not ours: left alone" if up() else "not running"
    subprocess.run(["kill", str(pid)], check=False)
    for _ in range(30):
        if not up():
            return "stopped"
        time.sleep(0.5)
    return "asked to stop"
