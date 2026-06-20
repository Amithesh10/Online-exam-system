# 🎓 Online Exam System with AI Face Proctoring

A secure, AI-proctored online examination system with real-time face detection, multi-language code execution, and a native desktop application — built with Python, Flask, and MediaPipe.

> Built by **Amithesh**

---

## ✨ Features

### 🔐 Authentication
- Secure student login with username & password
- Show/hide password toggle

### 📝 MCQ Section
- Clean, interactive multiple-choice question interface
- Live answer tracking with progress indicator
- Instant evaluation on submission

### 💻 Coding Section
- Built-in multi-language code editor
- **Supports Python, C, and Java** with real compilation and execution
- Starter code templates for each language
- Per-language code persistence (switching languages doesn't erase your work)

### ⏱️ Timed Exam
- 10-minute countdown timer
- Visual warning when time is running low
- Auto-submits when time expires

### 👁️ AI-Powered Proctoring
- Real-time face detection using **Google MediaPipe**
- Live webcam feed displayed in the exam interface
- Detects when no face is visible (5-second grace period before flagging)
- Detects multiple faces (unauthorized presence)
- Violation counter: **1 → 2 → 3 strikes**
- Auto-submits exam after 3 proctoring violations

### 📊 Results
- Animated score ring with percentage breakdown
- MCQ score, coding score, and proctoring violations summary
- Pass/Fail verdict

### 🖥️ Desktop Application
- Packaged as a standalone Windows `.exe` using PyWebView + PyInstaller
- No browser or separate Python installation required for end users
- Native desktop window with exit confirmation

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| AI / Computer Vision | Google MediaPipe Face Detection |
| Code Execution | Python `subprocess`, GCC (C), JDK (Java) |
| Desktop Packaging | PyWebView, PyInstaller |

---

## 📁 Project Structure

```
exam-portal/
├── app.py               # Desktop app launcher (PyWebView + Flask)
├── backend.py            # Flask server — routes, auth, code execution
├── exam_portal.spec      # PyInstaller build configuration
├── questions.json        # Exam questions (MCQ + coding)
├── users.json             # Student login credentials
├── exam_icon.ico          # Application icon
├── templates/
│   └── index.html         # Frontend UI (single-page application)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- GCC (for C code execution) — [MinGW](https://www.mingw-w64.org/) on Windows
- JDK (for Java code execution) — optional, app degrades gracefully if missing

### Installation

```bash
git clone https://github.com/<your-username>/exam-portal.git
cd exam-portal
pip install flask pywebview
```

### Run as a web app

```bash
python backend.py
```
Then open **http://127.0.0.1:5000** in your browser.

### Run as a desktop app

```bash
python app.py
```
This launches a native desktop window — no browser required.

---

## 📦 Building the Windows Executable

```bash
pip install pyinstaller
pyinstaller exam_portal.spec --clean
```

The standalone executable will be created at:
```
dist/ExamPortal.exe
```

This bundles everything — Flask, the UI, questions, and credentials — into a single file that runs on any Windows machine without requiring Python.

---

## ⚙️ Configuration

### Adding/editing exam questions

Edit `questions.json`:

```json
{
  "id": 1,
  "type": "mcq",
  "question": "What is the output of print(type([]))?",
  "options": ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"],
  "answer": "<class 'list'>"
}
```

For coding questions, set `"type": "coding"` and omit `"answer"`/`"options"`.

### Adding student credentials

Edit `users.json`:

```json
{
  "student1": "password123",
  "student2": "mypassword"
}
```

---

## 🧪 How Proctoring Works

1. On exam start, the browser requests camera access
2. MediaPipe's lightweight face detection model runs locally in-browser (no server upload of video)
3. If no face is detected for **5 consecutive seconds**, a violation is recorded
4. If **multiple faces** are detected, a violation is recorded
5. After **3 violations**, the exam auto-submits

---

## ⚠️ Disclaimer

This project was built for educational purposes. Code execution endpoints run user-submitted code via `subprocess` with a timeout — for production deployment with untrusted users, use proper sandboxing (Docker containers, gVisor, or a dedicated code execution service) instead of direct subprocess execution.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋 Author

**Amithesh**
Feel free to connect or reach out with questions/suggestions!
