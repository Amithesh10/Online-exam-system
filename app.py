"""
ExamPortal Desktop App
======================
Launches Flask in a background thread and opens the UI
in a native desktop window using PyWebView.

Run:  python app.py
Build exe: pyinstaller exam_portal.spec
"""

import threading
import time
import sys
import os

# ── CRITICAL: Set multiprocessing start method to 'spawn' fix for Windows exe ──
import multiprocessing
multiprocessing.freeze_support()

# ── Fix sys.executable so subprocess in backend points to python, not the .exe ──
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle — point to the bundled python interpreter
    BASE = sys._MEIPASS
    os.chdir(BASE)
    # Override sys.executable so run_python() uses the correct interpreter
    sys.executable = os.path.join(BASE, "python.exe")
    if not os.path.exists(sys.executable):
        # Fallback: use the system python
        import shutil
        sys.executable = shutil.which("python") or shutil.which("python3") or "python"
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE)

import webview
from backend import app as flask_app


def start_flask():
    """Run Flask silently in a daemon thread."""
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    flask_app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False,   # MUST be False inside PyWebView
        threaded=True         # Handle multiple requests (run code + exam simultaneously)
    )


def wait_for_flask(timeout=15):
    """Block until Flask is accepting connections."""
    import urllib.request
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen('http://127.0.0.1:5000/', timeout=1)
            return True
        except Exception:
            time.sleep(0.3)
    return False


class ExamAPI:
    """
    PyWebView JS API — intercepts navigation attempts
    so clicks never open a system browser tab.
    """
    pass


if __name__ == '__main__':
    # 1. Start Flask in background thread
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()

    # 2. Wait until Flask is ready
    if not wait_for_flask():
        print("ERROR: Flask server did not start in time.")
        sys.exit(1)

    # 3. Open the desktop window
    window = webview.create_window(
        title='ExamPortal - by Amithesh',
        url='http://127.0.0.1:5000/',
        width=1280,
        height=800,
        min_size=(900, 600),
        resizable=True,
        text_select=False,
        confirm_close=True,
        js_api=ExamAPI(),
    )

    # 4. Start PyWebView — use mshtml=False to force EdgeChromium (no new tab issues)
    webview.start(
        debug=False,
        private_mode=False,
    )