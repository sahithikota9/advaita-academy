from flask import Flask, render_template, request, redirect, session
import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load students (students.json is a LIST, not an object)
with open("students.json", "r") as f:
    students_data = json.load(f)

# Load exam results (also a LIST)
with open("results.json", "r") as f:
    results_data = json.load(f)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Check username & password
        for student in students_data:
            if student["username"] == username and student["password"] == password:
                session["username"] = username
                session["name"] = student["name"]
                return redirect("/dashboard")

        # Wrong credentials → show error
        return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/")

    username = session["username"]
    name = session["name"]

    student_exams = []

    # Find exams for this student
    for entry in results_data:
        if entry["username"] == username:
            student_exams = entry["exams"]
            break

    # Sort newest → oldest by exam_id
    student_exams = sorted(student_exams, key=lambda x: x["exam_id"], reverse=True)

    return render_template("dashboard.html", name=name, exams=student_exams)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)