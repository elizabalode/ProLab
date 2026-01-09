from flask import Flask, request, jsonify, send_from_directory, session, redirect
import sqlite3, os, random, datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, "app.db")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


# -----------------------------
# DB helpers
# -----------------------------
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db_from_schema() -> None:
    """
    Initialize DB by executing schema.sql (or schema.sql.txt if repo uses that naming).
    If neither exists, falls back to a minimal schema that matches required API.
    """
    schema_candidates = [
        os.path.join(APP_DIR, "schema.sql"),
        os.path.join(APP_DIR, "schema.sql.txt"),
    ]

    schema_path = next((p for p in schema_candidates if os.path.exists(p)), None)

    conn = db()
    try:
        if schema_path:
            with open(schema_path, "r", encoding="utf-8", errors="ignore") as f:
                sql = f.read()
            conn.executescript(sql)
        else:
            # Fallback minimal schema (should still work)
            conn.executescript("""
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS accounts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              account_id INTEGER UNIQUE NOT NULL,
              name TEXT,
              weight_kg REAL NOT NULL,
              height_cm REAL NOT NULL,
              age INTEGER NOT NULL DEFAULT 25,
              sex TEXT NOT NULL DEFAULT 'M',
              activity REAL NOT NULL DEFAULT 1.4,
              target_kcal REAL,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              updated_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS foods (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              fdc_id INTEGER UNIQUE,
              name TEXT NOT NULL,
              kcal_per_100g REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS meals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              type TEXT NOT NULL CHECK (type IN ('breakfast','lunch','dinner','snack'))
            );

            CREATE TABLE IF NOT EXISTS meal_items (
              meal_id INTEGER NOT NULL,
              food_id INTEGER NOT NULL,
              grams REAL NOT NULL,
              PRIMARY KEY (meal_id, food_id),
              FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
              FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS meal_plans (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              plan_date TEXT NOT NULL,
              breakfast_meal_id INTEGER NOT NULL,
              lunch_meal_id INTEGER NOT NULL,
              dinner_meal_id INTEGER NOT NULL,
              target_kcal REAL NOT NULL,
              created_at TEXT NOT NULL DEFAULT (datetime('now')),
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date
            ON meal_plans(user_id, plan_date, created_at);
            """)
        conn.commit()
    finally:
        conn.close()


init_db_from_schema()


# -----------------------------
# Auth / session helpers
# -----------------------------
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("account_id"):
            return jsonify({"error": "Unauthorized. Please login first."}), 401
        return fn(*args, **kwargs)
    return wrapper


def get_current_account_id():
    return session.get("account_id")


def get_profile(conn: sqlite3.Connection, account_id: int):
    return conn.execute("SELECT * FROM users WHERE account_id=? LIMIT 1", (account_id,)).fetchone()


# -----------------------------
# Nutrition logic
# -----------------------------
def mifflin_st_jeor(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    s = 5 if str(sex).upper() == "M" else -161
    return 10 * float(weight_kg) + 6.25 * float(height_cm) - 5 * int(age) + s


def daily_calories_target(user_row: sqlite3.Row) -> float:
    bmr = mifflin_st_jeor(
        user_row["weight_kg"],
        user_row["height_cm"],
        user_row["age"],
        user_row["sex"]
    )
    return float(bmr) * float(user_row["activity"])


def meal_kcal(conn: sqlite3.Connection, meal_id: int, factor: float = 1.0):
    """
    Returns: (meal_kcal_total, items[])
    Scaling happens in-memory (NO DB updates).
    """
    q = """
    SELECT mi.grams, f.kcal_per_100g, f.name
    FROM meal_items mi
    JOIN foods f ON f.id = mi.food_id
    WHERE mi.meal_id = ?
    """
    items = conn.execute(q, (meal_id,)).fetchall()

    total = 0.0
    out_items = []
    for it in items:
        grams = float(it["grams"]) * float(factor)
        kcal = (grams * float(it["kcal_per_100g"])) / 100.0
        total += kcal
        out_items.append({
            "name": it["name"],
            "grams": round(grams, 1),
            "kcal": round(kcal, 1)
        })

    return round(total, 1), out_items


def pick_meals(conn: sqlite3.Connection, seed: int):
    rnd = random.Random(seed)

    breakfast_meals = conn.execute("SELECT id FROM meals WHERE type='breakfast'").fetchall()
    lunch_meals = conn.execute("SELECT id FROM meals WHERE type='lunch'").fetchall()
    dinner_meals = conn.execute("SELECT id FROM meals WHERE type='dinner'").fetchall()

    if not breakfast_meals or not lunch_meals or not dinner_meals:
        raise RuntimeError(
            "Nav pietiekami daudz meal šablonu (breakfast/lunch/dinner). "
            "Pārbaudi, vai seed_data.sql ielādējās un vai meals.type ir pareizs."
        )

    return (
        rnd.choice(breakfast_meals)["id"],
        rnd.choice(lunch_meals)["id"],
        rnd.choice(dinner_meals)["id"],
    )


def get_latest_plan(conn: sqlite3.Connection, user_id: int, date_str: str):
    return conn.execute("""
        SELECT * FROM meal_plans
        WHERE user_id=? AND plan_date=?
        ORDER BY datetime(created_at) DESC, id DESC
        LIMIT 1
    """, (user_id, date_str)).fetchone()


def create_new_plan(conn: sqlite3.Connection, user_row: sqlite3.Row, date_str: str, target: float):
    """
    Always INSERT a new plan (history preserved).
    """
    count = conn.execute(
        "SELECT COUNT(*) AS n FROM meal_plans WHERE user_id=? AND plan_date=?",
        (int(user_row["id"]), date_str)
    ).fetchone()["n"]

    seed_str = f"{date_str}|{user_row['weight_kg']}|{user_row['height_cm']}|{user_row['age']}|{user_row['sex']}|{user_row['activity']}|{target}|v{count+1}"
    seed = abs(hash(seed_str)) % (2**31)

    b_id, l_id, d_id = pick_meals(conn, seed)

    cur = conn.execute("""
        INSERT INTO meal_plans(user_id, plan_date, breakfast_meal_id, lunch_meal_id, dinner_meal_id, target_kcal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (int(user_row["id"]), date_str, int(b_id), int(l_id), int(d_id), float(target)))

    conn.commit()
    return conn.execute("SELECT * FROM meal_plans WHERE id=?", (cur.lastrowid,)).fetchone()


def plan_response(conn: sqlite3.Connection, plan_row: sqlite3.Row):
    target = float(plan_row["target_kcal"])

    b0, _ = meal_kcal(conn, int(plan_row["breakfast_meal_id"]), 1.0)
    l0, _ = meal_kcal(conn, int(plan_row["lunch_meal_id"]), 1.0)
    d0, _ = meal_kcal(conn, int(plan_row["dinner_meal_id"]), 1.0)
    total0 = float(b0 + l0 + d0)

    factor = (target / total0) if total0 > 0 else 1.0
    factor = max(0.6, min(1.8, factor))

    b_kcal, b_items = meal_kcal(conn, int(plan_row["breakfast_meal_id"]), factor)
    l_kcal, l_items = meal_kcal(conn, int(plan_row["lunch_meal_id"]), factor)
    d_kcal, d_items = meal_kcal(conn, int(plan_row["dinner_meal_id"]), factor)

    total = round(b_kcal + l_kcal + d_kcal, 1)

    return {
        "plan_id": plan_row["id"],
        "date": plan_row["plan_date"],
        "created_at": plan_row["created_at"],
        "target_kcal": round(target, 0),
        "scale_factor": round(factor, 3),
        "meals": {
            "breakfast": {"kcal": b_kcal, "items": b_items},
            "lunch": {"kcal": l_kcal, "items": l_items},
            "dinner": {"kcal": d_kcal, "items": d_items},
        },
        "total_kcal": total
    }


# -----------------------------
# Pages (3 separate pages)
# -----------------------------
@app.get("/")
def home():
    return redirect("/login")


@app.get("/login")
def login_page():
    return send_from_directory(APP_DIR, "login.html")


@app.get("/profile-page")
@login_required
def profile_page():
    return send_from_directory(APP_DIR, "profile.html")


@app.get("/planner")
@login_required
def planner_page():
    return send_from_directory(APP_DIR, "planner.html")


# -----------------------------
# API: auth
# -----------------------------
@app.post("/api/register")
def api_register():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    conn = db()
    try:
        conn.execute(
            "INSERT INTO accounts(email, password_hash) VALUES (?, ?)",
            (email, generate_password_hash(password))
        )
        conn.commit()
        return jsonify({"ok": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "email already exists"}), 409
    finally:
        conn.close()


@app.post("/api/login")
def api_login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = db()
    try:
        acc = conn.execute("SELECT * FROM accounts WHERE email=?", (email,)).fetchone()
        if not acc or not check_password_hash(acc["password_hash"], password):
            return jsonify({"error": "invalid credentials"}), 401

        session["account_id"] = acc["id"]
        return jsonify({"ok": True})
    finally:
        conn.close()


@app.post("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
def api_me():
    return jsonify({"logged_in": bool(session.get("account_id"))})


# -----------------------------
# API: profile (create/update)
# -----------------------------
@app.get("/api/profile")
@login_required
def api_profile_get():
    account_id = int(get_current_account_id())
    conn = db()
    try:
        user = get_profile(conn, account_id)
        if not user:
            return jsonify({"has_profile": False})

        return jsonify({
            "has_profile": True,
            "user_id": user["id"],
            "name": user["name"],
            "weight_kg": user["weight_kg"],
            "height_cm": user["height_cm"],
            "age": user["age"],
            "sex": user["sex"],
            "activity": user["activity"],
            "target_kcal": user["target_kcal"],
            "updated_at": user["updated_at"],
        })
    finally:
        conn.close()


@app.post("/api/profile")
@login_required
def api_profile_post():
    data = request.json or {}
    account_id = int(get_current_account_id())

    try:
        weight = float(data["weight_kg"])
        height = float(data["height_cm"])
    except Exception:
        return jsonify({"error": "weight_kg and height_cm are required numbers"}), 400

    name = (data.get("name") or "User").strip()
    age = int(data.get("age") or 25)
    sex = (data.get("sex") or "M").upper()
    activity = float(data.get("activity") or 1.4)

    target_kcal = data.get("target_kcal")
    target_kcal = float(target_kcal) if target_kcal not in (None, "", "null") else None

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    conn = db()
    try:
        existing = get_profile(conn, account_id)
        if existing:
            conn.execute("""
                UPDATE users
                SET name=?, weight_kg=?, height_cm=?, age=?, sex=?, activity=?, target_kcal=?, updated_at=?
                WHERE account_id=?
            """, (name, weight, height, age, sex, activity, target_kcal, now, account_id))
            conn.commit()
            return jsonify({"ok": True, "user_id": existing["id"], "updated": True})
        else:
            cur = conn.execute("""
                INSERT INTO users(account_id, name, weight_kg, height_cm, age, sex, activity, target_kcal, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (account_id, name, weight, height, age, sex, activity, target_kcal, now, now))
            conn.commit()
            return jsonify({"ok": True, "user_id": cur.lastrowid, "created": True})
    finally:
        conn.close()


# Backward compatibility if some old UI still calls /api/user
@app.post("/api/user")
@login_required
def api_user_alias():
    return api_profile_post()


# -----------------------------
# API: plans (generate, load, history)
# -----------------------------
@app.get("/api/plan")
@login_required
def api_plan_get():
    """
    GET /api/plan?date=YYYY-MM-DD&mode=latest|new|id&plan_id=123
    """
    account_id = int(get_current_account_id())
    mode = (request.args.get("mode") or "latest").lower()

    conn = db()
    try:
        user = get_profile(conn, account_id)
        if not user:
            return jsonify({"error": "Nav profila. Vispirms saglabā profilu (/profile-page)."}), 400

        # mode=id -> load exact plan
        if mode == "id":
            plan_id = request.args.get("plan_id")
            if not plan_id:
                return jsonify({"error": "plan_id required for mode=id"}), 400

            plan = conn.execute(
                "SELECT * FROM meal_plans WHERE id=? AND user_id=?",
                (int(plan_id), int(user["id"]))
            ).fetchone()

            if not plan:
                return jsonify({"error": "Plan not found"}), 404

            return jsonify(plan_response(conn, plan))

        date_str = request.args.get("date") or datetime.date.today().isoformat()

        # target
        if user["target_kcal"] is not None:
            target = float(user["target_kcal"])
        else:
            target = float(daily_calories_target(user))
        target = round(target, 0)

        plan = None
        if mode != "new":
            plan = get_latest_plan(conn, int(user["id"]), date_str)

        if not plan:
            plan = create_new_plan(conn, user, date_str, target)

        return jsonify(plan_response(conn, plan))

    except Exception as e:
        # Make the real error visible to frontend (helps debugging)
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.get("/api/plans")
@login_required
def api_plans_list():
    account_id = int(get_current_account_id())
    limit = int(request.args.get("limit") or 30)

    conn = db()
    try:
        user = get_profile(conn, account_id)
        if not user:
            return jsonify({"error": "Nav profila."}), 400

        rows = conn.execute("""
            SELECT id, plan_date, target_kcal, created_at
            FROM meal_plans
            WHERE user_id=?
            ORDER BY datetime(created_at) DESC, id DESC
            LIMIT ?
        """, (int(user["id"]), limit)).fetchall()

        return jsonify({
            "plans": [
                {"plan_id": r["id"], "date": r["plan_date"], "target_kcal": r["target_kcal"], "created_at": r["created_at"]}
                for r in rows
            ]
        })
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
