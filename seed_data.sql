-- ===== FOODS (kcal / 100g) =====
INSERT INTO foods(name, kcal_per_100g) VALUES
('Oatmeal (dry)', 379),
('Milk 2%', 50),
('Banana', 89),
('Chicken breast', 165),
('Rice cooked', 130),
('Olive oil', 884),
('Tomato', 18),
('Egg', 155),
('Greek yogurt', 59),
('Apple', 52),
('Orange', 47),
('Strawberries', 32),
('Bread', 265),
('Cheese', 402),
('Peanut butter', 588),
('Tuna (canned, drained)', 132),
('Pasta cooked', 158),
('Potato boiled', 87),
('Salmon', 208),
('Minced beef (lean)', 250),
('Broccoli', 34),
('Cucumber', 15),
('Carrot', 41),
('Beans cooked', 127),
('Avocado', 160),
('Almonds', 579);

-- ===== MEALS (with type) =====
-- ===== MEALS (with type) =====
-- ===== MEALS (with type) =====
INSERT INTO meals(type, name) VALUES
('breakfast', 'Brokastis #1'),
('breakfast', 'Brokastis #2'),
('breakfast', 'Brokastis #3'),
('breakfast', 'Brokastis #4'),
('lunch',     'Pusdienas #1'),
('lunch',     'Pusdienas #2'),
('lunch',     'Pusdienas #3'),
('lunch',     'Pusdienas #4'),
('dinner',    'Vakariņas #1'),
('dinner',    'Vakariņas #2'),
('dinner',    'Vakariņas #3'),
('dinner',    'Vakariņas #4'),
('snack',     'Uzkoda #1'),
('snack',     'Uzkoda #2'),
('snack',     'Uzkoda #3');

-- ===== MEAL ITEMS (no IDs needed) =====

-- Brokastis #1
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 60  FROM meals m, foods f WHERE m.name='Brokastis #1' AND f.name='Oatmeal (dry)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 250 FROM meals m, foods f WHERE m.name='Brokastis #1' AND f.name='Milk 2%';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 120 FROM meals m, foods f WHERE m.name='Brokastis #1' AND f.name='Banana';

-- Brokastis #2
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 250 FROM meals m, foods f WHERE m.name='Brokastis #2' AND f.name='Greek yogurt';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Brokastis #2' AND f.name='Apple';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 15  FROM meals m, foods f WHERE m.name='Brokastis #2' AND f.name='Almonds';

-- Brokastis #3
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 120 FROM meals m, foods f WHERE m.name='Brokastis #3' AND f.name='Egg';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 80  FROM meals m, foods f WHERE m.name='Brokastis #3' AND f.name='Bread';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 70  FROM meals m, foods f WHERE m.name='Brokastis #3' AND f.name='Avocado';

-- Brokastis #4
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 60  FROM meals m, foods f WHERE m.name='Brokastis #4' AND f.name='Oatmeal (dry)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Brokastis #4' AND f.name='Strawberries';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 15  FROM meals m, foods f WHERE m.name='Brokastis #4' AND f.name='Peanut butter';

-- Pusdienas #1
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Pusdienas #1' AND f.name='Chicken breast';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Pusdienas #1' AND f.name='Rice cooked';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Pusdienas #1' AND f.name='Tomato';

-- Pusdienas #2
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 160 FROM meals m, foods f WHERE m.name='Pusdienas #2' AND f.name='Tuna (canned, drained)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Pusdienas #2' AND f.name='Beans cooked';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Pusdienas #2' AND f.name='Cucumber';

-- Pusdienas #3
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 220 FROM meals m, foods f WHERE m.name='Pusdienas #3' AND f.name='Pasta cooked';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Pusdienas #3' AND f.name='Minced beef (lean)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Pusdienas #3' AND f.name='Carrot';

-- Pusdienas #4
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Pusdienas #4' AND f.name='Chicken breast';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 250 FROM meals m, foods f WHERE m.name='Pusdienas #4' AND f.name='Potato boiled';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Pusdienas #4' AND f.name='Broccoli';

-- Vakariņas #1
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 160 FROM meals m, foods f WHERE m.name='Vakariņas #1' AND f.name='Minced beef (lean)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 220 FROM meals m, foods f WHERE m.name='Vakariņas #1' AND f.name='Potato boiled';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Vakariņas #1' AND f.name='Tomato';

-- Vakariņas #2
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 160 FROM meals m, foods f WHERE m.name='Vakariņas #2' AND f.name='Salmon';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Vakariņas #2' AND f.name='Rice cooked';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Vakariņas #2' AND f.name='Broccoli';

-- Vakariņas #3
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 160 FROM meals m, foods f WHERE m.name='Vakariņas #3' AND f.name='Tuna (canned, drained)';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 80  FROM meals m, foods f WHERE m.name='Vakariņas #3' AND f.name='Avocado';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Vakariņas #3' AND f.name='Cucumber';

-- Vakariņas #4
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Vakariņas #4' AND f.name='Chicken breast';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Vakariņas #4' AND f.name='Rice cooked';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 150 FROM meals m, foods f WHERE m.name='Vakariņas #4' AND f.name='Carrot';

-- Uzkoda #1
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 180 FROM meals m, foods f WHERE m.name='Uzkoda #1' AND f.name='Orange';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 20  FROM meals m, foods f WHERE m.name='Uzkoda #1' AND f.name='Almonds';

-- Uzkoda #2
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 70 FROM meals m, foods f WHERE m.name='Uzkoda #2' AND f.name='Bread';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 30 FROM meals m, foods f WHERE m.name='Uzkoda #2' AND f.name='Cheese';

-- Uzkoda #3
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 200 FROM meals m, foods f WHERE m.name='Uzkoda #3' AND f.name='Greek yogurt';
INSERT INTO meal_items(meal_id, food_id, grams)
SELECT m.id, f.id, 120 FROM meals m, foods f WHERE m.name='Uzkoda #3' AND f.name='Strawberries';
