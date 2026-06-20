from flask import Flask, request, jsonify, render_template
import json, os, sys, subprocess, tempfile, shutil, re

app = Flask(__name__, template_folder="templates")

TIMEOUT = 15  # seconds per execution

# ── Hide console window on Windows for all subprocess calls ──
CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

# ─────────────────────────── Runners ───────────────────────────

def run_python(code):
    """Run Python code via a temp file — works correctly on Windows with multiline code."""
    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, "solution.py")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run(
            [sys.executable, src],
            capture_output=True, text=True, timeout=TIMEOUT,
            cwd=tmpdir, encoding="utf-8", errors="replace",
            creationflags=CREATION_FLAGS
        )
        out = result.stdout or ""
        err = result.stderr or ""
        return (out + err).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (15s limit)"
    except Exception as e:
        return f"Error: {e}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def run_c(code):
    if not shutil.which("gcc"):
        return "Error: GCC not found. Install MinGW on Windows."
    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, "main.c")
        exe = os.path.join(tmpdir, "main.exe" if os.name == "nt" else "main")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        comp = subprocess.run(
            ["gcc", src, "-o", exe, "-lm"],
            capture_output=True, text=True, timeout=TIMEOUT,
            encoding="utf-8", errors="replace",
            creationflags=CREATION_FLAGS
        )
        if comp.returncode != 0:
            return "Compilation Error:\n" + comp.stderr.strip()
        run = subprocess.run(
            [exe],
            capture_output=True, text=True, timeout=TIMEOUT,
            encoding="utf-8", errors="replace",
            creationflags=CREATION_FLAGS
        )
        return (run.stdout + run.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timed out after 15 seconds."
    except Exception as e:
        return f"Error: {e}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def run_java(code):
    if not shutil.which("javac"):
        return "Error: JDK not found. Install Java JDK."
    match = re.search(r'public\s+class\s+(\w+)', code)
    classname = match.group(1) if match else "Main"
    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, f"{classname}.java")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)
        comp = subprocess.run(
            ["javac", src],
            capture_output=True, text=True, timeout=TIMEOUT,
            encoding="utf-8", errors="replace",
            creationflags=CREATION_FLAGS
        )
        if comp.returncode != 0:
            return "Compilation Error:\n" + comp.stderr.strip()
        run = subprocess.run(
            ["java", "-cp", tmpdir, classname],
            capture_output=True, text=True, timeout=TIMEOUT,
            encoding="utf-8", errors="replace",
            creationflags=CREATION_FLAGS
        )
        return (run.stdout + run.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timed out after 15 seconds."
    except Exception as e:
        return f"Error: {e}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


RUNNERS = {"python": run_python, "c": run_c, "java": run_java}

# ─────────────────────────── Data ───────────────────────────

BASE = os.path.dirname(os.path.abspath(__file__))

def load_json(f):
    with open(os.path.join(BASE, f)) as fp:
        return json.load(fp)

QUESTIONS = load_json("questions.json")
USERS     = load_json("users.json")

# ─────────────────────────── Routes ───────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)
        if USERS.get(data.get("username","").strip()) == data.get("password",""):
            return jsonify({"status": "success"})
        return jsonify({"status": "failed"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/questions", methods=["GET"])
def get_questions():
    return jsonify([
        {"id": q["id"], "type": q.get("type","mcq"),
         "question": q["question"], "options": q.get("options",[])}
        for q in QUESTIONS
    ])

@app.route("/submit", methods=["POST"])
def submit_exam():
    data        = request.get_json(force=True)
    mcq_answers = data.get("mcq_answers", {})
    coding_ans  = data.get("coding_answer", "")
    mcq_qs      = [q for q in QUESTIONS if q.get("type") == "mcq"]
    score       = sum(1 for q in mcq_qs if mcq_answers.get(str(q["id"])) == q.get("answer"))
    total       = len(mcq_qs)
    coding_score = 0
    if [q for q in QUESTIONS if q.get("type") == "coding"]:
        if "def "   in coding_ans: coding_score += 1
        if "return" in coding_ans: coding_score += 1
    return jsonify({"score": score + coding_score, "total": total + 2})

@app.route("/run", methods=["POST"])
def run_code():
    data     = request.get_json(force=True)
    code     = data.get("code", "").strip()
    language = data.get("language", "python").lower()
    if not code:
        return jsonify({"output": "No code provided."})
    runner = RUNNERS.get(language)
    if not runner:
        return jsonify({"output": f"Unsupported language: {language}"})
    return jsonify({"output": runner(code)})

if __name__ == "__main__":
    print("\n Exam server running --> http://127.0.0.1:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)      