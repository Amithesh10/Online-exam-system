from flask import Flask, request, jsonify, render_template
import json
import os
import sys
import subprocess
import tempfile
import shutil
import re

app = Flask(__name__, template_folder="templates", static_folder="static")

TIMEOUT = 15

CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

BASE = os.path.dirname(os.path.abspath(__file__))


# -------------------- Code Runners --------------------

def run_python(code):
    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, "solution.py")

        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        result = subprocess.run(
            [sys.executable, src],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=tmpdir,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATION_FLAGS
        )

        output = (result.stdout or "") + (result.stderr or "")
        return output.strip() or "(no output)"

    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out."

    except Exception as e:
        return f"Error: {e}"

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def run_c(code):
    if not shutil.which("gcc"):
        return "Error: GCC not available on server."

    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, "main.c")
        exe = os.path.join(tmpdir, "main")

        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        compile_result = subprocess.run(
            ["gcc", src, "-o", exe, "-lm"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATION_FLAGS
        )

        if compile_result.returncode != 0:
            return "Compilation Error:\n" + compile_result.stderr.strip()

        run_result = subprocess.run(
            [exe],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATION_FLAGS
        )

        return ((run_result.stdout or "") + (run_result.stderr or "")).strip() or "(no output)"

    except subprocess.TimeoutExpired:
        return "Error: Timed out after 15 seconds."

    except Exception as e:
        return f"Error: {e}"

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def run_java(code):
    if not shutil.which("javac"):
        return "Error: Java JDK not available on server."

    match = re.search(r"public\s+class\s+(\w+)", code)
    classname = match.group(1) if match else "Main"

    tmpdir = tempfile.mkdtemp()
    try:
        src = os.path.join(tmpdir, f"{classname}.java")

        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        compile_result = subprocess.run(
            ["javac", src],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATION_FLAGS
        )

        if compile_result.returncode != 0:
            return "Compilation Error:\n" + compile_result.stderr.strip()

        run_result = subprocess.run(
            ["java", "-cp", tmpdir, classname],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATION_FLAGS
        )

        return ((run_result.stdout or "") + (run_result.stderr or "")).strip() or "(no output)"

    except subprocess.TimeoutExpired:
        return "Error: Timed out after 15 seconds."

    except Exception as e:
        return f"Error: {e}"

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


RUNNERS = {
    "python": run_python,
    "c": run_c,
    "java": run_java
}


# -------------------- JSON Loader --------------------

def load_json(filename):
    path = os.path.join(BASE, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


QUESTIONS = load_json("questions.json")
USERS = load_json("users.json")


# -------------------- Routes --------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if USERS.get(username) == password:
            return jsonify({"status": "success"})

        return jsonify({"status": "failed"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/questions", methods=["GET"])
def get_questions():
    safe_questions = []

    for q in QUESTIONS:
        safe_questions.append({
            "id": q["id"],
            "type": q.get("type", "mcq"),
            "question": q["question"],
            "options": q.get("options", [])
        })

    return jsonify(safe_questions)


@app.route("/submit", methods=["POST"])
def submit_exam():
    data = request.get_json(force=True)

    mcq_answers = data.get("mcq_answers", {})
    coding_answer = data.get("coding_answer", "")

    mcq_questions = [q for q in QUESTIONS if q.get("type") == "mcq"]

    score = 0

    for q in mcq_questions:
        qid = str(q["id"])
        if mcq_answers.get(qid) == q.get("answer"):
            score += 1

    total = len(mcq_questions)

    coding_score = 0
    coding_questions = [q for q in QUESTIONS if q.get("type") == "coding"]

    if coding_questions:
        if "def " in coding_answer:
            coding_score += 1
        if "return" in coding_answer:
            coding_score += 1

    return jsonify({
        "score": score + coding_score,
        "total": total + 2
    })


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json(force=True)

    code = data.get("code", "").strip()
    language = data.get("language", "python").lower()

    if not code:
        return jsonify({"output": "No code provided."})

    runner = RUNNERS.get(language)

    if not runner:
        return jsonify({"output": f"Unsupported language: {language}"})

    output = runner(code)

    return jsonify({"output": output})


# -------------------- Main --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
