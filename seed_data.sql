INSERT INTO foods(name, kcal_per_100g) VALUES
('Oatmeal (dry)', 379),
('Milk 2%', 50),
('Banana', 89),
('Chicken breast', 165),
('Rice cooked', 130),
('Olive oil', 884),
('Tomato', 18);

INSERT INTO meals(name) VALUES ('Brokastis #1'), ('Pusdienas #1'), ('Vakariņas #1');

-- brokastis #1 (meal_id=1)
INSERT INTO meal_items(meal_id, food_id, grams) VALUES
(1, 1, 60),
(1, 2, 250),
(1, 3, 120);

-- pusdienas #1 (meal_id=2)
INSERT INTO meal_items(meal_id, food_id, grams) VALUES
(2, 4, 180),
(2, 5, 200),
(2, 7, 150);

-- vakariņas #1 (meal_id=3)
INSERT INTO meal_items(meal_id, food_id, grams) VALUES
(3, 4, 160),
(3, 5, 150),
(3, 6, 10),
(3, 7, 200);
