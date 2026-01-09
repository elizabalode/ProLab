PRAGMA foreign_keys = ON;

-- ========== ACCOUNTS (AUTH) ==========
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ========== USER PROFILE ==========
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

-- ========== FOODS ==========
CREATE TABLE IF NOT EXISTS foods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  fdc_id INTEGER UNIQUE,
  name TEXT NOT NULL,
  kcal_per_100g REAL NOT NULL
);

-- ========== MEALS (templates) ==========
CREATE TABLE IF NOT EXISTS meals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL CHECK (type IN ('breakfast','lunch','dinner','snack')),
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meal_items (
  meal_id INTEGER NOT NULL,
  food_id INTEGER NOT NULL,
  grams REAL NOT NULL,
  PRIMARY KEY (meal_id, food_id),
  FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
  FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE
);

-- ========== MEAL PLANS (HISTORY) ==========
-- Svarīgi: šeit vairs NAV PRIMARY KEY (user_id, plan_date),
-- jo mums vajag saglabāt vairākus plānus vienam datumam (vēsture).
CREATE TABLE IF NOT EXISTS meal_plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  plan_date TEXT NOT NULL,
  breakfast_meal_id INTEGER NOT NULL,
  lunch_meal_id INTEGER NOT NULL,
  dinner_meal_id INTEGER NOT NULL,
  target_kcal REAL NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);


CREATE INDEX IF NOT EXISTS idx_meal_plans_user_date
ON meal_plans(user_id, plan_date, created_at);
