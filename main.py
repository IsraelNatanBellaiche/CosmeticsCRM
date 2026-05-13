from flask import Flask, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "crm_secret_key_123"

DB = "crm.db"
ADMIN_PASSWORD = "1234"

# ---------- DB ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            notes TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            date TEXT,
            time TEXT,
            service TEXT,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        return "סיסמה שגויה"

    return """
    <html dir='rtl'>
    <body style='font-family:Arial;text-align:center;margin-top:100px'>
        <h2>כניסה למערכת CRM</h2>
        <form method='post'>
            <input type='password' name='password' placeholder='סיסמה'>
            <button type='submit'>כניסה</button>
        </form>
    </body>
    </html>
    """


# ---------- HOME ----------
@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect("/login")

    conn = sqlite3.connect(DB)
    customers = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    appointments = conn.execute("SELECT * FROM appointments ORDER BY date, time").fetchall()
    conn.close()

    return f"""
    <html dir='rtl'>
    <head>
    <meta charset='utf-8'>
    <title>מיכל בלעיש CRM עסקי</title>
    <style>
        body{{font-family:Arial;background:linear-gradient(180deg,#fff,#fff4f9);max-width:1200px;margin:auto;padding:20px}}
        h1{{color:#c2185b}}
        .box{{background:white;padding:15px;border-radius:12px;margin:10px 0;box-shadow:0 2px 10px rgba(0,0,0,0.05)}}
        input,select,textarea{{width:100%;padding:10px;margin:5px 0;border-radius:10px;border:1px solid #ddd}}
        button{{background:#c2185b;color:white;padding:10px;border:0;border-radius:10px;cursor:pointer}}
        .item{{border:1px solid #eee;padding:10px;margin:8px 0;border-radius:10px}}
        a.whatsapp{{background:#25D366;color:white;padding:10px;border-radius:10px;text-decoration:none}}
        .grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
    </style>
    </head>
    <body>

    <h1>מיכל בלעיש - הקוסמטיקאית שלך 💅</h1>

    <a class='whatsapp' href='https://wa.me/972547259965' target='_blank'>📱 וואטסאפ מהיר</a>
    <a href='/logout' style='margin-right:10px'>יציאה</a>

    <div class='box'>
    <h2>לקוח חדש</h2>
    <form method='post' action='/add_customer'>
        <input name='name' placeholder='שם'>
        <input name='phone' placeholder='טלפון'>
        <select name='service'>
            <option>טיפול פנים</option>
            <option>מיקרובליידינג</option>
            <option>לק ג׳ל</option>
            <option>שעווה</option>
            <option>גבות</option>
            <option>מוצר</option>
        </select>
        <textarea name='notes' placeholder='הערות'></textarea>
        <button>הוסף</button>
    </form>
    </div>

    <div class='box'>
    <h2>קביעת תור</h2>
    <form method='post' action='/add_appointment'>
        <input name='customer_name' placeholder='שם לקוחה'>
        <input name='phone' placeholder='טלפון'>
        <input name='date' type='date'>
        <input name='time' type='time'>
        <select name='service'>
            <option>טיפול פנים</option>
            <option>מיקרובליידינג</option>
            <option>לק ג׳ל</option>
            <option>שעווה</option>
        </select>
        <textarea name='notes'></textarea>
        <button>קבע תור</button>
    </form>
    </div>

    <div class='box'>
    <h2>יומן תורים</h2>
    """ + "".join([
        f"<div class='item'><b>{a[1]}</b><br>{a[3]} {a[4]}<br>{a[5]}</div>"
        for a in appointments
    ]) + """
    </div>

    <div class='box'>
    <h2>לקוחות</h2>
    """ + "".join([
        f"<div class='item'><b>{c[1]}</b> | {c[2]}<br>{c[3]}<br>{c[4]}<br>{c[5]}</div>"
        for c in customers
    ]) + """
    </div>

    </body>
    </html>
    """


# ---------- ADD ----------
@app.route('/add_customer', methods=['POST'])
def add_customer():
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO customers(name,phone,service,notes,created_at) VALUES (?,?,?,?,?)",
                 (request.form['name'], request.form['phone'], request.form['service'], request.form['notes'], datetime.now().strftime('%d/%m/%Y %H:%M')))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO appointments(customer_name,phone,date,time,service,notes) VALUES (?,?,?,?,?,?)",
                 (request.form['customer_name'], request.form['phone'], request.form['date'], request.form['time'], request.form['service'], request.form['notes']))
    conn.commit()
    conn.close()
    return redirect('/')


# ---------- AUTH ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- RUN ----------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
