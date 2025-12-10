from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import json
import os
from datetime import datetime

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(APP_ROOT, "students.json")

app = Flask(__name__)
app.secret_key = "replace-this-with-a-long-random-secret"  # change before production


def load_students():
    with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_students(data):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def current_student_obj():
    if "username" not in session:
        return None
    students = load_students()
    for s in students:
        if s["username"] == session["username"]:
            return s
    return None


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    # POST - try login
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    students = load_students()
    for s in students:
        if s["username"] == username and s["password"] == password:
            # login success
            session["username"] = username
            session["name"] = s.get("name", "Student")
            return redirect(url_for("dashboard"))
    # failure
    return render_template("login.html", error="Invalid username or password")


@app.route("/dashboard")
@login_required
def dashboard():
    student = current_student_obj()
    # show latest exams first (by date string if present); otherwise keep latest added order.
    exams = student.get("exams", [])
    # try to sort by datetime if exam has date
    def exam_key(e):
        d = e.get("date")
        if d:
            try:
                return datetime.fromisoformat(d)
            except:
                return datetime.min
        return datetime.min
    exams_sorted = sorted(exams, key=exam_key, reverse=True)
    return render_template("dashboard.html", student=student, exams=exams_sorted)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/add_score", methods=["POST"])
@login_required
def add_score():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data"}), 400

    exam_name = data.get("exam_name", "Exam").strip()
    math = int(data.get("math", 0))
    physics = int(data.get("physics", 0))
    chemistry = int(data.get("chemistry", 0))
    # clamp between 0 and 100
    math = max(0, min(100, math))
    physics = max(0, min(100, physics))
    chemistry = max(0, min(100, chemistry))
    total = math + physics + chemistry
    date_now = datetime.utcnow().isoformat()

    students = load_students()
    for s in students:
        if s["username"] == session["username"]:
            exam = {
                "exam_name": exam_name,
                "date": date_now,
                "math": math,
                "physics": physics,
                "chemistry": chemistry,
                "total": total
            }
            # insert at beginning to keep latest-first
            s.setdefault("exams", [])
            s["exams"].insert(0, exam)
            save_students(students)
            return jsonify({"success": True, "exam": exam})
    return jsonify({"success": False, "error": "Student not found"}), 404


# optional API to fetch student data (used by frontend)
@app.route("/api/student")
@login_required
def api_student():
    s = current_student_obj()
    if not s:
        return jsonify({"success": False}), 404
    return jsonify({"success": True, "student": s})


if __name__ == "__main__":
    # create students.json if missing
    if not os.path.exists(STUDENTS_FILE):
        # expecting user to paste the provided students.json manually; otherwise fail loudly
        raise RuntimeError("students.json not found. Please add students.json in repository root.")
    app.run(host="0.0.0.0", port=5000, debug=True)
