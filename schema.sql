CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  weight_kg REAL NOT NULL,
  height_cm REAL NOT NULL,
  age INTEGER DEFAULT 25,
  sex TEXT DEFAULT 'M',
  activity REAL DEFAULT 1.4,
  target_kcal REAL
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
  FOREIGN KEY (meal_id) REFERENCES meals(id),
  FOREIGN KEY (food_id) REFERENCES foods(id)
);

CREATE TABLE IF NOT EXISTS meal_plans (
  user_id INTEGER NOT NULL,
  plan_date TEXT NOT NULL,
  breakfast_meal_id INTEGER NOT NULL,
  lunch_meal_id INTEGER NOT NULL,
  dinner_meal_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, plan_date),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
