import os
import sys
import time
import socket
import threading
import webbrowser
import subprocess

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def get_free_port(preferred_port=8050):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", preferred_port)) != 0:
            return preferred_port

    try:
        out = subprocess.check_output(
            f'netstat -aon | findstr ":{preferred_port}" | findstr "LISTENING"',
            shell=True,
            text=True
        )
        for line in out.strip().split("\n"):
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = parts[-1]
                if pid.isdigit() and int(pid) != os.getpid():
                    print(f"  [*] Freeing port {preferred_port} (terminating old PID {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", preferred_port)) != 0:
                return preferred_port
    except Exception:
        pass

    for p in range(preferred_port + 1, preferred_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                print(f"  [!] Port {preferred_port} busy, automatically shifted to port {p}")
                return p
    return preferred_port

active_port = get_free_port(8050)

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://127.0.0.1:{active_port}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    import uvicorn

    print("\n" + "=" * 65)
    print("  🎨 AIRCANVAS AI — TOUCHLESS GESTURE WHITEBOARD")
    print("=" * 65)
    print(f"  ✨ Vision Engine        : MediaPipe Hands (60 FPS)")
    print(f"  🧠 AI Shape Snapping    : Active (Circle, Rect, Triangle, Line)")
    print(f"  🎙️ Voice Control AI     : Web Speech API & NLP Engine")
    print(f"  🌐 Local Web Dashboard  : http://127.0.0.1:{active_port}")
    print(f"  💡 Opening your default browser automatically...")
    print("=" * 65 + "\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("AirCanvas.app:app", host="127.0.0.1", port=active_port, reload=False, log_level="info")
