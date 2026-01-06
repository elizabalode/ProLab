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
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s

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
        out_items.append({
            "name": it["name"],
            "grams": round(float(it["grams"]), 1),
            "kcal": round(float(kcal), 1)
        })

    return round(total, 1), out_items

def scale_meal(conn, meal_id, factor, min_factor=0.6, max_factor=1.8):
    factor = max(min_factor, min(max_factor, float(factor)))
    conn.execute(
        "UPDATE meal_items SET grams = grams * ? WHERE meal_id = ?",
        (factor, meal_id)
    )

def ensure_plan(conn, user_id, date_str, user_row):
    # Vienmēr pārrakstām plānu šai dienai (lai mainoties parametriem, mainās arī plāns)
    conn.execute(
        "DELETE FROM meal_plans WHERE user_id=? AND plan_date=?",
        (user_id, date_str)
    )
    conn.commit()

    # Seed = datums + user parametri (lai mainās plāns, ja mainās svars/augums/aktivitāte/vecums)
    seed_str = f"{date_str}|{user_row['weight_kg']}|{user_row['height_cm']}|{user_row['age']}|{user_row['sex']}|{user_row['activity']}|{user_row['target_kcal']}"
    seed = abs(hash(seed_str)) % (2**31)
    rnd = random.Random(seed)

    # Izvēle pēc type (lai vakariņas nav brokastīs)
    breakfast_meals = conn.execute("SELECT id FROM meals WHERE type='breakfast'").fetchall()
    lunch_meals     = conn.execute("SELECT id FROM meals WHERE type='lunch'").fetchall()
    dinner_meals    = conn.execute("SELECT id FROM meals WHERE type='dinner'").fetchall()

    if not breakfast_meals or not lunch_meals or not dinner_meals:
        raise RuntimeError("Trūkst meals ar type breakfast/lunch/dinner. Pārbaudi seed_data.sql un schema.sql.")

    breakfast = rnd.choice(breakfast_meals)["id"]
    lunch     = rnd.choice(lunch_meals)["id"]
    dinner    = rnd.choice(dinner_meals)["id"]

    conn.execute(
        """
        INSERT INTO meal_plans
        (user_id, plan_date, breakfast_meal_id, lunch_meal_id, dinner_meal_id)
        VALUES (?, ?, ?, ?, ?)
        """,
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

    target_kcal = data.get("target_kcal")
    target_kcal = float(target_kcal) if target_kcal not in (None, "", "null") else None

    conn = db()
    cur = conn.execute(
        "INSERT INTO users(name, weight_kg, height_cm, age, sex, activity, target_kcal) VALUES (?,?,?,?,?,?,?)",
        (name, weight, height, age, sex, activity, target_kcal)
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

    # 1) user
    user = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 2) target kcal (user ievada -> izmanto, citādi aprēķina)
    user_target = user["target_kcal"]
    if user_target is not None:
        target = float(user_target)
    else:
        target = float(daily_calories_target(user))
    target = round(target, 0)

    # 3) generate plan
    plan = ensure_plan(conn, user_id, date_str, user)

    # 4) initial total
    b0, _ = meal_kcal(conn, plan["breakfast_meal_id"])
    l0, _ = meal_kcal(conn, plan["lunch_meal_id"])
    d0, _ = meal_kcal(conn, plan["dinner_meal_id"])
    total0 = b0 + l0 + d0

    # 5) scale portions to reach target (approximately)
    if total0 > 0:
        factor = target / total0
        scale_meal(conn, plan["breakfast_meal_id"], factor)
        scale_meal(conn, plan["lunch_meal_id"], factor)
        scale_meal(conn, plan["dinner_meal_id"], factor)
        conn.commit()

    # 6) final totals after scaling
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
