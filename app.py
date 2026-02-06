from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


@app.route("/")
def home():
    return render_template("login.html")
    
@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/patient")
def patient():
    return render_template("patient.html")

@app.route("/register")
def register():
    return render_template("register.html")
        
def get_db():
    return sqlite3.connect("database.db")

# ---------- DATABASE ----------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        doctor TEXT,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()

        if user:
            session["user"] = user[1]
            session["role"] = user[4]

            if user[4] == "patient":
                return redirect("/patient")
            elif user[4] == "doctor":
                return redirect("/doctor")
            else:
                return redirect("/admin")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users VALUES (NULL,?,?,?,?)",
                    (name, email, password, role))
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("register.html")

@patient_bp.route("/patient", methods=["GET", "POST"])
def patient():
    if request.method == "POST":
        doctor = request.form["doctor"]
        date = request.form["date"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO appointments VALUES (NULL,?,?,?,?)",
                    (session["user"], doctor, date, "Pending"))
        conn.commit()
        conn.close()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE patient=?", (session["user"],))
    data = cur.fetchall()

    return render_template("patient.html", data=data)

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        status = request.form["status"]
        app_id = request.form["id"]
        cur.execute("UPDATE appointments SET status=? WHERE id=?", (status, app_id))
        conn.commit()

    cur.execute("SELECT * FROM appointments WHERE doctor=?", (session["user"],))
    data = cur.fetchall()

    return render_template("doctor.html", data=data)

@app.route("/admin")
def admin():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments")
    data = cur.fetchall()
    return render_template("admin.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if  __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0",port=10000)
