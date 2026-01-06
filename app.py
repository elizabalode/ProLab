from flask import Flask, request, jsonify, send_from_directory
import sqlite3, os, random, datetime

APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, "app.db")

app = Flask(__name__)

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def mifflin_st_jeor(weight_kg, height_cm, age, sex):
    s = 5 if sex.upper() == "M" else -161
    return 10*weight_kg + 6.25*height_cm - 5*age + s

def daily_calories_target(user_row):
    bmr = mifflin_st_jeor(
        user_row["weight_kg"],
        user_row["height_cm"],
        user_row["age"],
        user_row["sex"]
    )
    return bmr * float(user_row["activity"])

def meal_kcal(conn, meal_id):
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
        kcal = (it["grams"] * it["kcal_per_100g"]) / 100.0
        total += kcal
        out_items.append({"name": it["name"], "grams": it["grams"], "kcal": round(kcal, 1)})
    return round(total, 1), out_items

def ensure_plan(conn, user_id, date_str):
    plan = conn.execute(
        "SELECT * FROM meal_plans WHERE user_id=? AND plan_date=?",
        (user_id, date_str)
    ).fetchone()
    if plan:
        return plan

    meals = conn.execute("SELECT id FROM meals").fetchall()
    if len(meals) < 3:
        raise RuntimeError("DB nav pietiekami daudz meals (vajag vismaz 3).")

    seed = int(date_str.replace("-", ""))
    rnd = random.Random(seed)

    breakfast = rnd.choice(meals)["id"]
    lunch = rnd.choice(meals)["id"]
    dinner = rnd.choice(meals)["id"]

    conn.execute(
        "INSERT INTO meal_plans(user_id, plan_date, breakfast_meal_id, lunch_meal_id, dinner_meal_id) VALUES (?,?,?,?,?)",
        (user_id, date_str, breakfast, lunch, dinner)
    )
    conn.commit()

    return conn.execute(
        "SELECT * FROM meal_plans WHERE user_id=? AND plan_date=?",
        (user_id, date_str)
    ).fetchone()

@app.get("/")
def index():
    return send_from_directory(APP_DIR, "index.html")

@app.post("/api/user")
def create_user():
    data = request.json
    name = data.get("name", "User")
    weight = float(data["weight_kg"])
    height = float(data["height_cm"])
    age = int(data.get("age", 25))
    sex = data.get("sex", "M")
    activity = float(data.get("activity", 1.4))

    conn = db()
    cur = conn.execute(
        "INSERT INTO users(name, weight_kg, height_cm, age, sex, activity) VALUES (?,?,?,?,?,?)",
        (name, weight, height, age, sex, activity)
    )
    conn.commit()
    user_id = cur.lastrowid
    return jsonify({"user_id": user_id})

@app.get("/api/plan")
def get_plan():
    user_id = int(request.args.get("user_id", "1"))
    date_str = request.args.get("date")
    if not date_str:
        date_str = datetime.date.today().isoformat()

    conn = db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    plan = ensure_plan(conn, user_id, date_str)

    target = round(daily_calories_target(user), 0)

    b_kcal, b_items = meal_kcal(conn, plan["breakfast_meal_id"])
    l_kcal, l_items = meal_kcal(conn, plan["lunch_meal_id"])
    d_kcal, d_items = meal_kcal(conn, plan["dinner_meal_id"])

    total = round(b_kcal + l_kcal + d_kcal, 1)

    return jsonify({
        "date": date_str,
        "target_kcal": target,
        "meals": {
            "breakfast": {"kcal": b_kcal, "items": b_items},
            "lunch": {"kcal": l_kcal, "items": l_items},
            "dinner": {"kcal": d_kcal, "items": d_items},
        },
        "total_kcal": total
    })

if __name__ == "__main__":
    app.run(debug=True)
