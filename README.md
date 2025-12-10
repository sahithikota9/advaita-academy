# advaita-academy
# Coaching Results Portal

Simple Flask app to let students (5-digit username & password) log in and view/add exam results.

## Run locally
1. Create a Python venv:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows

2. Install:
   pip install -r requirements.txt

3. Ensure `students.json` is present (provided). Edit `app.py` secret key.

4. Run:
   python app.py

Open http://localhost:5000

## Deploy to Render
- Create a new Web Service (Python).
- Connect repo.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Ensure `students.json` is in repo root.

## Notes
- Passwords are stored as plain text for simplicity — for production, store hashed passwords.
- `students.json` is the single data store. For concurrency or many users, move to a real DB.
