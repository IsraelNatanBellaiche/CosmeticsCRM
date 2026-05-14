from flask import Flask, request, redirect, session, render_template
import sqlite3
from datetime import datetime
import urllib.parse
import os

app = Flask(__name__)
app.secret_key = "crm_secret_key_123"

# Detect environment: Render or Local
if os.environ.get("RENDER"):
    DB = "/tmp/crm.db"   # Render environment
else:
    DB = "crm.db"        # Local environment

ADMIN_PASSWORD = "1234"

MICHAL_PHONE = "0547259965"
ADDRESS_TEXT = "אידלסון 19"
ADDRESS_MAP_LINK = "https://www.google.com/maps/search/" + urllib.parse.quote(ADDRESS_TEXT)


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            service TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


def normalize_phone(phone: str) -> str:
    phone = phone.replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    return phone


@app.route("/")
def landing():
    return render_template("home.html", title="מיכל בלעיש - קוסמטיקאית")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        date = request.form.get("date", "").strip()
        time_ = request.form.get("time", "").strip()
        notes = request.form.get("notes", "").strip()

        conn = sqlite3.connect(DB)
        conn.execute("""
            INSERT INTO appointments(name, phone, date, time, service, notes, created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (
            name,
            phone,
            date,
            time_,
            service,
            notes,
            datetime.now().strftime('%d/%m/%Y %H:%M')
        ))
        conn.commit()
        conn.close()

        michal_msg = (
            f"תור חדש נקבע:\n"
            f"שם: {name}\n"
            f"טלפון: {phone}\n"
            f"שירות: {service}\n"
            f"תאריך: {date}\n"
            f"שעה: {time_}\n"
            f"הערות: {notes}"
        )
        michal_link = "https://wa.me/" + normalize_phone(MICHAL_PHONE) + "?text=" + urllib.parse.quote(michal_msg)

        client_msg = (
            f"היי {name}! התור שלך נקבע בהצלחה ❤️\n"
            f"שירות: {service}\n"
            f"תאריך: {date}\n"
            f"שעה: {time_}\n"
            f"נתראה!"
        )
        client_link = "https://wa.me/" + normalize_phone(phone) + "?text=" + urllib.parse.quote(client_msg)

        return render_template(
            "book_success.html",
            name=name,
            michal_link=michal_link,
            client_link=client_link,
            address_link=ADDRESS_MAP_LINK,
            CLIENT_URL=CLIENT_URL,
            OWNER_URL=OWNER_URL
        )

    return render_template("book.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/dashboard")
        return render_template("login.html", title="כניסה - שגיאה")

    return render_template("login.html", title="כניסה")


@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("dashboard.html", appointments=rows)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# URLs קבועים
CLIENT_URL = "https://cosmeticscrm.onrender.com/client"
OWNER_URL = "https://cosmeticscrm.onrender.com/owner"


@app.route("/client")
def client_page():
    return render_template("client.html", title="כניסת לקוחה")


@app.route("/owner")
def owner_page():
    return render_template("owner.html", title="כניסת בעלים")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
