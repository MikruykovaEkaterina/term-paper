import sqlite3

def create_database():
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS types_of_dishes (
        dish_type_code INTEGER PRIMARY KEY AUTOINCREMENT,
        name_of_the_type_of_dish TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dishes (
        dish_code INTEGER PRIMARY KEY AUTOINCREMENT,
        denomination TEXT,
        price REAL,
        dish_type_code INTEGER,
        FOREIGN KEY (dish_type_code) REFERENCES types_of_dishes(dish_type_code) ON DELETE CASCADE,
        UNIQUE (denomination)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS components (
        component_code INTEGER PRIMARY KEY AUTOINCREMENT,
        denomination TEXT,
        caloric_content INTEGER,
        price REAL,
        weight INTEGER,
        CHECK (caloric_content >= 0),
        CHECK (price >= 0),
        CHECK (weight >= 0)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS composition_of_the_dish (
        dish_code INTEGER,
        component_code INTEGER,
        PRIMARY KEY (dish_code, component_code),
        FOREIGN KEY (dish_code) REFERENCES dishes(dish_code) ON DELETE CASCADE,
        FOREIGN KEY (component_code) REFERENCES components(component_code) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS microelements (
        microelement_code INTEGER PRIMARY KEY AUTOINCREMENT,
        denomination TEXT UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS composition_of_components (
        component_code INTEGER,
        microelement_code INTEGER,
        quantity_per_100g INTEGER,
        PRIMARY KEY (component_code, microelement_code),
        FOREIGN KEY (component_code) REFERENCES components(component_code) ON DELETE CASCADE,
        FOREIGN KEY (microelement_code) REFERENCES microelements(microelement_code) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_set_of_microelements (
        microelement_code INTEGER PRIMARY KEY,
        quantity_in_mg INTEGER,
        FOREIGN KEY (microelement_code) REFERENCES microelements(microelement_code) ON DELETE CASCADE
    )
    ''')

    # Вставка данных
    cursor.executemany('''
    INSERT INTO types_of_dishes (name_of_the_type_of_dish) VALUES (?)
    ''', [
        ('Appetizer',),
        ('Main Course',),
        ('Dessert',),
        ('Beverage',),
        ('Side Dish',),
        ('Soup',),
        ('Salad',),
        ('Bread',),
        ('Starter',),
        ('Entree',),
        ('Snack',),
        ('Desert',),
        ('Cocktail',),
        ('Wine',),
        ('Diet',),
        ('Gluten-Free',),
        ('Vegan',),
        ('Vegetarian',),
        ('Pasta',),
        ('Seafood',),
        ('Meat',) ])

    cursor.executemany('''
    INSERT INTO dishes (denomination, price, dish_type_code) VALUES (?, ?, ?)
    ''', [
        ('Grilled Chicken', 12.99, 2),
        ('Caesar Salad', 8.50, 7),
        ('Beef Steak', 19.99, 2),
        ('Spaghetti Bolognese', 11.50, 19),
        ('Vegetable Stir-Fry', 9.75, 2),
        ('Salmon with Rice', 14.50, 20),
        ('Chicken Soup', 6.99, 6),
        ('Veggie Burger', 7.50, 2),
        ('Fruit Salad', 5.99, 3),
        ('Greek Yogurt Parfait', 6.50, 3),
        ('Steak with Mashed Potatoes', 16.99, 2),
        ('Sushi Platter', 15.00, 1),
        ('Pasta Primavera', 10.50, 19),
        ('BBQ Ribs', 14.99, 2),
        ('Vegetable Lasagna', 11.50, 19),
        ('Tuna Salad Sandwich', 7.50, 1),
        ('Cod Fish Tacos', 8.50, 1),
        ('Beef Tendon', 13.50, 2),
        ('Vegetable Stir-Fry 2', 9.75, 2),
        ('Shrimp Scampi', 12.50, 20) ])

    cursor.executemany('''
    INSERT INTO components (denomination, caloric_content, price, weight) VALUES (?, ?, ?, ?)
    ''', [
        ('Chicken Breast', 165, 15.99, 200),
        ('Rice', 130, 2.50, 150),
        ('Broccoli', 55, 3.00, 120),
        ('Salmon', 208, 20.00, 170),
        ('Spinach', 23, 1.50, 90),
        ('Beef', 250, 18.00, 220),
        ('Quinoa', 120, 4.00, 140),
        ('Avocado', 160, 5.00, 100),
        ('Tomato', 18, 1.00, 80),
        ('Lettuce', 15, 0.75, 70),
        ('Greek Yogurt', 100, 3.50, 150),
        ('Olive Oil', 884, 10.00, 100),
        ('Almonds', 579, 8.00, 50),
        ('Banana', 89, 0.50, 120),
        ('Orange', 47, 0.40, 130),
        ('Milk', 42, 1.20, 200),
        ('Eggs', 143, 2.00, 100),
        ('Pasta', 131, 2.50, 150),
        ('Tuna', 133, 5.00, 140),
        ('Cod', 91, 6.00, 180)])

    cursor.executemany('''
    INSERT INTO microelements (denomination) VALUES (?)
    ''', [
        ('Calcium',),
        ('Iron',),
        ('Vitamin C',),
        ('Vitamin D',),
        ('Potassium',),
        ('Magnesium',),
        ('Zinc',),
        ('Vitamin A',),
        ('Fiber',),
        ('Protein',),
        ('Carbohydrates',),
        ('Fat',),
        ('Sodium',),
        ('Phosphorus',),
        ('Vitamin B12',),
        ('Vitamin E',),
        ('Copper',),
        ('Manganese',),
        ('Selenium',),
        ('Chromium',)])

    cursor.executemany('''
    INSERT INTO composition_of_the_dish (dish_code, component_code) VALUES (?, ?)
    ''', [
        (1, 1), # Grilled Chicken contains Chicken Breast
        (1, 14), # Grilled Chicken contains Milk (e.g., for sauce)
        (2, 10), # Caesar Salad contains Lettuce
        (2, 9), # Caesar Salad contains Tomato
        (3, 6), # Beef Steak contains Beef
        (4, 2), # Spaghetti Bolognese contains Rice (assuming pasta)
        (5, 3), # Vegetable Stir-Fry contains Broccoli
        (5, 4), # Vegetable Stir-Fry contains Salmon (if included)
        (6, 4), # Salmon with Rice contains Salmon
        (6, 2), # Salmon with Rice contains Rice
        (7, 1), # Chicken Soup contains Chicken Breast
        (7, 11), # Chicken Soup contains Greek Yogurt (e.g., for creaminess)
        (8, 15), # Veggie Burger contains Orange (e.g., for flavor)
        (8, 3), # Veggie Burger contains Broccoli
        (9, 16), # Fruit Salad contains Olive Oil (dressing)
        (9, 12), # Fruit Salad contains Olive Oil (dressing)
        (10, 11), # Greek Yogurt Parfait contains Greek Yogurt
        (10, 17), # Greek Yogurt Parfait contains Almonds
        (11, 6), # Steak with Mashed Potatoes contains Beef
        (11, 2)])# Steak with Mashed Potatoes contains Rice (mashed potatoes)


    cursor.executemany('''
    INSERT INTO composition_of_components (component_code, microelement_code, quantity_per_100g) VALUES (?, ?, ?)
    ''', [
        (1, 1, 20), # Chicken Breast contains Calcium 20mg/100g
        (1, 7, 2), # Chicken Breast contains Zinc 2mg/100g
        (2, 5, 100), # Rice contains Potassium 100mg/100g
        (2, 12, 5), # Rice contains Fat 5mg/100g
        (3, 3, 50), # Broccoli contains Vitamin C 50mg/100g
        (3, 4, 5), # Broccoli contains Vitamin D 5mg/100g
        (4, 1, 10), # Salmon contains Calcium 10mg/100g
        (4, 16, 1), # Salmon contains Vitamin E 1mg/100g
        (5, 3, 25), # Spinach contains Vitamin C 25mg/100g
        (5, 9, 2), # Spinach contains Fiber 2mg/100g
        (6, 10, 20), # Beef contains Protein 20mg/100g
        (6, 14, 5), # Beef contains Phosphorus 5mg/100g
        (7, 5, 80), # Quinoa contains Potassium 80mg/100g
        (7, 10, 4), # Quinoa contains Protein 4mg/100g
        (8, 3, 15), # Avocado contains Vitamin C 15mg/100g
        (8, 12, 15), # Avocado contains Fat 15mg/100g
        (9, 3, 10), # Tomato contains Vitamin C 10mg/100g
        (9, 5, 20), # Tomato contains Potassium 20mg/100g
        (10, 1, 5), # Lettuce contains Calcium 5mg/100g
        (10, 3, 5)]) # Lettuce contains Vitamin C 5mg/100g

    cursor.executemany('''
    INSERT INTO daily_set_of_microelements (microelement_code, quantity_in_mg) VALUES (?, ?)
    ''', [
        (1, 1000), # Calcium 1000mg/day
        (2, 18), # Iron 18mg/day
        (3, 90), # Vitamin C 90mg/day
        (4, 15), # Vitamin D 15mg/day
        (5, 3500), # Potassium 3500mg/day
        (6, 400), # Magnesium 400mg/day
        (7, 11), # Zinc 11mg/day
        (8, 900), # Vitamin A 900mg/day
        (9, 25), # Fiber 25mg/day
        (10, 50), # Protein 50mg/day
        (11, 130), # Carbohydrates 130mg/day
        (12, 70), # Fat 70mg/day
        (13, 2300), # Sodium 2300mg/day
        (14, 700), # Phosphorus 700mg/day
        (15, 2.4), # Vitamin B12 2.4mg/day
        (16, 15), # Vitamin E 15mg/day
        (17, 900), # Copper 900mg/day
        (18, 2.3), # Manganese 2.3mg/day
        (19, 55), # Selenium 55mg/day
        (20, 35)]) # Chromium 35mg/day

    cursor.execute('''
       CREATE VIEW IF NOT EXISTS dish_nutrition_view AS
       SELECT d.denomination AS dish_name,
              SUM(c.caloric_content) AS total_calories,
              SUM(comp.quantity_per_100g) AS total_microelements
       FROM dishes d
       JOIN composition_of_the_dish cd ON d.dish_code = cd.dish_code
       JOIN components c ON cd.component_code = c.component_code
       JOIN composition_of_components comp ON c.component_code = comp.component_code
       GROUP BY d.dish_code
       ''')

    # View for Sales Report by Dish Type
    cursor.execute('''
       CREATE VIEW IF NOT EXISTS sales_by_dish_type_view AS
       SELECT td.name_of_the_type_of_dish AS dish_type,
              SUM(d.price) AS total_sales
       FROM dishes d
       JOIN types_of_dishes td ON d.dish_type_code = td.dish_type_code
       GROUP BY td.name_of_the_type_of_dish
       ''')

    # View for Inventory Report
    cursor.execute('''
       CREATE VIEW IF NOT EXISTS inventory_report_view AS
       SELECT c.denomination AS component_name,
              SUM(c.weight) AS total_weight,
              SUM(c.price * c.weight / 100) AS total_cost
       FROM components c
       GROUP BY c.component_code
       ''')
    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_dishes_dish_type_code ON dishes(dish_type_code);
       ''')

    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_composition_dish_code ON composition_of_the_dish(dish_code);
       ''')

    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_composition_component_code ON composition_of_the_dish(component_code);
       ''')

    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_components_component_code ON components(component_code);
       ''')

    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_composition_components_component_code ON composition_of_components(component_code);
       ''')

    cursor.execute('''
       CREATE INDEX IF NOT EXISTS idx_components_denomination ON components(denomination);
       ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()