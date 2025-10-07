import sqlite3
import time

SECONDS_PER_DAY = 86400

# Connects to pantry database
def open_db():
    conn = sqlite3.connect('flask_backend/pantry.db')
    # Returns queries as Row objects (similar to dictionary)
    conn.row_factory = sqlite3.Row
    # Enforces correct foreign keys
    conn.execute("PRAGMA foreign_keys = 1")
    return conn

# Creates the following tables:
# units: stores units of measurements for food. e.g. tbsp., cups, oz
# ingredients: stores different types of ingredients and their nutritional values
# pantry: stores physical ingredients from user's kitchen
# recipes: stores user and LLM generated recipes
# recipe_ingredients: stores all the required ingredients + quantities for recipes table
def create_tables():
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("""CREATE TABLE units (
                    id INTEGER PRIMARY KEY,
                    unit TEXT NOT NULL UNIQUE
                    ) STRICT""")
        
        c.execute("""CREATE TABLE ingredients (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    serving_size REAL NOT NULL,
                    unit_of_measurement TEXT NOT NULL REFERENCES units(unit),
                    calories REAL,
                    total_fat REAL,
                    sodium REAL,
                    total_carbohydrate REAL,
                    total_sugars REAL,
                    protein REAL,
                    cost REAL,
                    shelf_life INTEGER
                    ) STRICT""")

        c.execute("""CREATE TABLE pantry (
                    id INTEGER PRIMARY KEY,
                    ingredient_name TEXT NOT NULL REFERENCES ingredients(name),
                    quantity REAL NOT NULL,
                    purchase_date INTEGER DEFAULT (unixepoch()),
                    expiry_date INTEGER
                    ) STRICT""")

        c.execute("""CREATE TABLE recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    meal_type TEXT,
                    prep_time INTEGER,
                    cook_time INTEGER,
                    instructions TEXT NOT NULL,
                    servings INTEGER NOT NULL DEFAULT (1)
                    ) STRICT""")

        c.execute("""CREATE TABLE recipe_ingredients (
                    recipe_name TEXT NOT NULL REFERENCES recipes(name) ON DELETE CASCADE,            
                    ingredient_name TEXT NOT NULL REFERENCES ingredients(name),
                    quantity REAL NOT NULL,
                    unit_of_measurement TEXT NOT NULL REFERENCES units(unit),
                    PRIMARY KEY (recipe_name, ingredient_name)
                    ) STRICT""")
        conn.commit()
    except sqlite3.Error as error:
        print(f"Failed to create tables: ", error)
    finally:
        conn.close()

# Function to initialize common units to units table    
def init_units():
    conn = open_db()
    c = conn.cursor()
    units = [("ml",), ("L",), ("tsp.",), ("tbsp.",), ("cup(s)",), ("fl oz",), ("pint(s)",), ("g",), ("lb",), ("oz",), ("clove(s)",), ("piece(s)",),]
    try:
        c.executemany("INSERT INTO units (unit) VALUES (?)", units)
        conn.commit()
    except sqlite3.Error as error:
        print(f"Failed to setup units table: ", error)
    finally:
        conn.close()

# Inserts into ingredients table.
def insert_ingredient(name, serving_size, unit_of_measurement, calories=None, total_fat=None, sodium=None,
                      total_carbohydrate=None, total_sugars=None, protein=None, cost=None, shelf_life=None):
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO ingredients (
                    name, serving_size, unit_of_measurement, calories, total_fat, sodium, 
                    total_carbohydrate, total_sugars, protein, cost, shelf_life)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (name, serving_size, unit_of_measurement, calories, total_fat, sodium, 
                    total_carbohydrate, total_sugars, protein, cost, shelf_life,))
        conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Failed to insert {name}: ", error)
        return False
    finally:
        conn.close()

# Inserts into pantry table. 
# Purchase date defaults to current time.
# If expiry date not specified, will be set to purchase date + ingredient shelf life. 
# If ingredient has no shelf life, expiry date will be NULL
def add_to_pantry(ingredient_name, quantity, purchase_date=round(time.time()), expiry_date=None):
    conn = open_db()
    c = conn.cursor()
    # check ingredient_name is in ingredients table
    ingredient = get_ingredient(ingredient_name)
    if not ingredient:
        print(f"Ingredient {ingredient_name} not found")
        conn.close()
        return False
    
    # sets expiry date based on ingredient shelf life and current time
    if not expiry_date:
        shelf_life = ingredient['shelf_life']
        if shelf_life: 
            expiry_date = round(purchase_date + shelf_life * SECONDS_PER_DAY)
    
    try:
        c.execute("""INSERT INTO pantry (
                    ingredient_name, quantity, purchase_date, expiry_date)
                    VALUES (?, ?, ?, ?)""", (ingredient["name"], quantity, purchase_date, expiry_date,))
        conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Failed to insert {ingredient_name} to pantry: ", error)
        return False
    finally:
        conn.close()

# Inserts recipe into recipes table 
# instructions: string
# ingredients: list of (ingredient, quantity, unit) tuples
def add_recipe(recipe_name, instructions, ingredients, meal_type=None, prep_time=None, cook_time=None, servings=1):
    conn = open_db()
    c = conn.cursor()
    # add recipe
    try:
        c.execute("""INSERT INTO recipes (name, meal_type, prep_time, cook_time, instructions, servings)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (recipe_name, meal_type, prep_time, cook_time, instructions, servings))
    except sqlite3.Error as error:
        print(f"Failed to insert {recipe_name}: ", error)
        conn.close()
        return False
    
    # add recipe ingredients
    for quant_ingredient in ingredients:
        ingredient_name, quantity, unit_of_measurement = quant_ingredient
        ingredient = get_ingredient(ingredient_name)
        if not ingredient:
            print(f"Ingredient {ingredient_name} not found")
            conn.close()
            return False
        
        try:
            c.execute("""INSERT INTO recipe_ingredients (recipe_name, ingredient_name, quantity, unit_of_measurement)
                        VALUES (?, ?, ?, ?)""", 
                        (recipe_name, ingredient["name"], quantity, unit_of_measurement))
        except sqlite3.Error as error:
            print(f"Failed to insert {ingredient_name} for recipe {recipe_name}: ", error)
            c.execute("PRAGMA foreign_key_check")
            print("Foreign key check:", c.fetchall())
            conn.close()
            return False
            
    conn.commit()
    conn.close()
    return True

# Removes ingredient from ingredients table
def remove_ingredient(ingredient_name):
    conn = open_db()
    c = conn.cursor()
    if len(get_ingredient(ingredient_name)) == 0:
        print(f"Ingredient {ingredient_name} not found")
        conn.close()
        return False
    
    try:
        c.execute("DELETE FROM ingredients WHERE name = ?", (ingredient_name,))
        conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Failed to delete {ingredient_name}: ", error)
        return False
    finally:
        conn.close()

# Removes ingredient from pantry table 
def remove_from_pantry(id):
    conn = open_db()
    c = conn.cursor()
    if len(get_from_pantry(id)) == 0:
        print("Item ID not found")
        conn.close()
        return False
    
    try:
        c.execute("DELETE FROM pantry WHERE id = ?", (id,))
        conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Failed to delete id:{id} from pantry: ", error)
        return False
    finally:
        conn.close()

# Removes recipe from recipes table
# All coresponding ingredients from recipe_ingredients table will automatically be deleted
def remove_recipe(recipe_name):
    conn = open_db()
    c = conn.cursor()
    if len(get_recipe(recipe_name)) == 0:
        print(f"Recipe for {recipe_name} not found")
        conn.close()
        return False
    
    try:
        c.execute("DELETE FROM recipes WHERE name = ?", (recipe_name,))
        conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Failed to delete {recipe_name}: ", error)
        return False
    finally:    
        conn.close()

# Returns the corresponding row in the ingredients table (list)
def get_ingredient(ingredient_name):
    ingredient_name = ingredient_name.lower()
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM ingredients WHERE LOWER(name) = ?", (ingredient_name,))
    except sqlite3.Error as error:
        print(f"Failed to get {ingredient_name}: ", error)
        conn.close()
        return
    ingredient=c.fetchone()
    
    conn.close()
    ingredient = dict(ingredient) if ingredient else None
    return ingredient

# Returns the corresponding row in the pantry table (list)
def get_from_pantry(id):
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM pantry WHERE id = ?", (id,))
    except sqlite3.Error as error:
        print(f"Failed to get id:{id} from pantry: ", error)
        conn.close()
        return
    ingredient=c.fetchone()
    
    conn.close()
    ingredient = dict(ingredient) if ingredient else None
    return ingredient

# Returns Dict[recipe:Dict, ingredients:List[Dict]]
def get_recipe(recipe_name):
    recipe_name = recipe_name.lower()
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM recipes WHERE LOWER(name) = ?", (recipe_name,))
    except sqlite3.Error as error:
        print(f"Failed to get {recipe_name}: ", error)
        conn.close()
        return None
    recipe = c.fetchone()
    
    try:
        c.execute("SELECT * FROM recipe_ingredients WHERE LOWER(recipe_name) = ?", (recipe_name,))
    except sqlite3.Error as error:
        print(f"Failed to get recipe ingredients: ", error)
        conn.close()
        return None
    ingredients = c.fetchall()
    
    conn.close()
    recipe = dict(recipe) if recipe else None
    return {"recipe":recipe, "ingredients":[dict(row) for row in ingredients]}

# filters recipes by preptime, required ingredients, meal type, and whether or not ingredients are available in pantry
# prep_time: (mintime, maxtime)
# cook_time: (mintime, maxtime)
# ingredients: [ingredient_name, ingredient_name...]
# meal_type: breakfast, lunch, dinner, snack
# returns List[Dict[recipe:Dict, recipe_ingredients:List[Dict]]]
def filter_recipes(prep_time=None, cook_time=None, ingredients=None, meal_type=None, ingredients_available=False):
    conn = open_db()
    c = conn.cursor()
    
    # Base query
    query = "SELECT * FROM recipes"
    conditions = []
    params = []
    
    # Complete query
    if prep_time:
        conditions.append("prep_time BETWEEN ? AND ?")
        params.extend(prep_time)
        
    if cook_time:
        conditions.append("cook_time BETWEEN ? AND ?")
        params.extend(cook_time)
        
    if meal_type:
        conditions.append("LOWER(meal_type) = ?")
        params.append(meal_type.lower())

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Query recipes table
    try:
        c.execute(query, params)
        recipes = c.fetchall()
    except sqlite3.Error as error:
        print(f"Failed to filter recipes: ", error)
        conn.close()
        return

    # Filter recipes
    filtered_recipes = []
    for recipe in recipes:
        recipe_name = recipe["name"]
        # Get ingredients used by recipe
        try:
            c.execute("SELECT * FROM recipe_ingredients WHERE recipe_name = ?", (recipe_name,))
        except sqlite3.Error as error:
            print(f"Failed to get recipe ingredients: ", error)
            conn.close()
            continue
        recipe_ingredients = c.fetchall()
        ingredient_names = {row["ingredient_name"].lower() for row in recipe_ingredients}
    
        # Check if recipe contains required ingredients
        if ingredients:
            if not set(ingredients).issubset(ingredient_names):
                continue

        # Check if ingredients are available in pantry
        if ingredients_available:
            try:
                c.execute("SELECT ingredient_name FROM pantry WHERE expiry_date IS NULL OR expiry_date > ?", (round(time.time()),))
                available_ingredients = {row["ingredient_name"].lower() for row in c.fetchall()}
            except sqlite3.Error as error:
                print(f"Failed to get pantry ingredients: ", error)
                continue

            if not ingredient_names.issubset(available_ingredients):
                continue

        filtered_recipes.append({"recipe":dict(recipe), "ingredients":[dict(ingredient) for ingredient in recipe_ingredients]})

    conn.close()
    return filtered_recipes

# Gets ingredients from pantry that are not currently expired but will expire in specified number of days
def get_expiring(days):
    conn = open_db()
    c = conn.cursor()
    cut_off = round(time.time() + days * SECONDS_PER_DAY)
    
    try:
        c.execute("SELECT ingredient_name FROM pantry WHERE expiry_date >= ? AND expiry_date < ?", (round(time.time()), cut_off,))
    except sqlite3.Error as error:
        print(f"Failed to get expiring ingredients: ", error)
        conn.close()
        return
    ingredients = c.fetchall()
    
    conn.close()
    ingredients = [dict(row) for row in ingredients]
    return ingredients

# Gets currently expired ingredients
def get_expired():
    conn = open_db()
    c = conn.cursor()
    try:
        c.execute("SELECT ingredient_name FROM pantry WHERE expiry_date < ?", (round(time.time()),))
    except sqlite3.Error as error:
        print(f"Failed to get expired ingredients: ", error)
        conn.close()
        return
    ingredients = c.fetchall()
    
    conn.close()
    ingredients = [dict(row) for row in ingredients]
    return ingredients

# EXAMPLE USE CASE
open_db()
# get_recipe("spaghetti_carbonara")
# create_tables()
# init_units()
                    
# insert_ingredient("Olive Oil", 1, "tbsp.", calories=119, total_fat=14,sodium=0, total_carbohydrate=0, total_sugars=0, protein=0)
# insert_ingredient("Pancetta", 1, "oz", calories=147, total_fat=15, sodium=9.1, total_carbohydrate=0, total_sugars=0, protein=2.6, shelf_life=7)
# insert_ingredient("Garlic", 1, "clove(s)", calories=4.5, total_fat=0, sodium=0.5, total_carbohydrate=1, total_sugars=0, protein=0.2)
# insert_ingredient("Eggs", 1, "piece(s)", calories=72, total_fat=4.8, sodium=71, total_carbohydrate=0.4, total_sugars=0.2, protein=6.3)
# insert_ingredient("Parmesan Cheese", 1, "tbsp.", calories=21, total_fat=1.4, sodium=90, total_carbohydrate=0.7, total_sugars=0, protein=1.4)
# insert_ingredient("Spaghetti", 2, "oz", calories=210, total_fat=0.9, sodium=3.4, total_carbohydrate=42, total_sugars=1.5, protein=7.4)

# Additional common kitchen ingredients
# insert_ingredient("Butter", 1, "tbsp.", calories=102, total_fat=11.5, sodium=91, total_carbohydrate=0, total_sugars=0, protein=0.1)
# insert_ingredient("Milk", 1, "cup(s)", calories=103, total_fat=2.4, sodium=107, total_carbohydrate=12, total_sugars=12, protein=8)
# insert_ingredient("Salt", 1, "tsp.", calories=0, total_fat=0, sodium=2325, total_carbohydrate=0, total_sugars=0, protein=0)
# insert_ingredient("Black Pepper", 1, "tsp.", calories=6, total_fat=0.1, sodium=0, total_carbohydrate=1.5, total_sugars=0, protein=0.2)
# insert_ingredient("Onion", 1, "piece(s)", calories=44, total_fat=0.1, sodium=4, total_carbohydrate=10, total_sugars=4.7, protein=1.2)
# insert_ingredient("Tomato", 1, "piece(s)", calories=22, total_fat=0.2, sodium=6, total_carbohydrate=4.8, total_sugars=3.2, protein=1.1)
# insert_ingredient("Carrot", 1, "piece(s)", calories=25, total_fat=0.1, sodium=42, total_carbohydrate=6, total_sugars=2.9, protein=0.6)
# insert_ingredient("Broccoli", 1, "cup(s)", calories=55, total_fat=0.6, sodium=50, total_carbohydrate=11, total_sugars=2.2, protein=3.7)
# insert_ingredient("Chicken Breast", 1, "oz", calories=47, total_fat=1.1, sodium=20, total_carbohydrate=0, total_sugars=0, protein=8.8, shelf_life=2)
# insert_ingredient("Ground Beef", 1, "oz", calories=77, total_fat=6.5, sodium=21, total_carbohydrate=0, total_sugars=0, protein=5.2, shelf_life=2)
# insert_ingredient("Rice", 1, "cup(s)", calories=206, total_fat=0.4, sodium=1, total_carbohydrate=45, total_sugars=0.1, protein=4.3)
# insert_ingredient("Bread", 1, "piece(s)", calories=79, total_fat=1, sodium=147, total_carbohydrate=14, total_sugars=1.6, protein=2.8)
# insert_ingredient("Cheddar Cheese", 1, "oz", calories=114, total_fat=9.4, sodium=174, total_carbohydrate=0.4, total_sugars=0.1, protein=7)
# insert_ingredient("Lettuce", 1, "cup(s)", calories=5, total_fat=0.1, sodium=10, total_carbohydrate=1, total_sugars=0.5, protein=0.5)
# insert_ingredient("Spinach", 1, "cup(s)", calories=7, total_fat=0.1, sodium=24, total_carbohydrate=1.1, total_sugars=0.1, protein=0.9)
# insert_ingredient("Bell Pepper", 1, "piece(s)", calories=24, total_fat=0.2, sodium=2, total_carbohydrate=6, total_sugars=4.2, protein=1)
# insert_ingredient("Cucumber", 1, "piece(s)", calories=16, total_fat=0.1, sodium=2, total_carbohydrate=3.8, total_sugars=1.7, protein=0.7)
# insert_ingredient("Zucchini", 1, "piece(s)", calories=33, total_fat=0.6, sodium=16, total_carbohydrate=6.1, total_sugars=4.9, protein=2.4)
# insert_ingredient("Basil", 1, "tbsp.", calories=1, total_fat=0, sodium=0.3, total_carbohydrate=0.1, total_sugars=0, protein=0.2)
# insert_ingredient("Oregano", 1, "tsp.", calories=6, total_fat=0.3, sodium=0.4, total_carbohydrate=1.4, total_sugars=0, protein=0.2)
# insert_ingredient("Thyme", 1, "tsp.", calories=3, total_fat=0.1, sodium=0.5, total_carbohydrate=0.8, total_sugars=0, protein=0.1)
# insert_ingredient("Cinnamon", 1, "tsp.", calories=6, total_fat=0, sodium=0.4, total_carbohydrate=2.1, total_sugars=0.1, protein=0.1)
# insert_ingredient("Sugar", 1, "tsp.", calories=16, total_fat=0, sodium=0, total_carbohydrate=4.2, total_sugars=4.2, protein=0)
# insert_ingredient("Brown Sugar", 1, "tsp.", calories=17, total_fat=0, sodium=1, total_carbohydrate=4.5, total_sugars=4.5, protein=0)
# insert_ingredient("Honey", 1, "tbsp.", calories=64, total_fat=0, sodium=1, total_carbohydrate=17, total_sugars=17, protein=0.1)
# insert_ingredient("Maple Syrup", 1, "tbsp.", calories=52, total_fat=0, sodium=2, total_carbohydrate=13, total_sugars=12, protein=0)
# insert_ingredient("Peanut Butter", 1, "tbsp.", calories=94, total_fat=8, sodium=76, total_carbohydrate=3.2, total_sugars=1.5, protein=4)
# insert_ingredient("Mayonnaise", 1, "tbsp.", calories=94, total_fat=10, sodium=88, total_carbohydrate=0.1, total_sugars=0, protein=0.1)
# insert_ingredient("Ketchup", 1, "tbsp.", calories=15, total_fat=0, sodium=160, total_carbohydrate=4, total_sugars=3.2, protein=0.2)
# insert_ingredient("Soy Sauce", 1, "tbsp.", calories=10, total_fat=0, sodium=879, total_carbohydrate=0.8, total_sugars=0.1, protein=1.3)
# insert_ingredient("Vinegar", 1, "tbsp.", calories=3, total_fat=0, sodium=1, total_carbohydrate=0.1, total_sugars=0, protein=0)
# insert_ingredient("Lemon Juice", 1, "tbsp.", calories=4, total_fat=0, sodium=1, total_carbohydrate=1.3, total_sugars=0.4, protein=0.1)
# insert_ingredient("Lime Juice", 1, "tbsp.", calories=4, total_fat=0, sodium=1, total_carbohydrate=1.3, total_sugars=0.4, protein=0.1)
# insert_ingredient("Chili Powder", 1, "tsp.", calories=8, total_fat=0.4, sodium=0.8, total_carbohydrate=1.4, total_sugars=0, protein=0.3)
# insert_ingredient("Coriander", 1, "tsp.", calories=5, total_fat=0.3, sodium=0.6, total_carbohydrate=0.9, total_sugars=0, protein=0.2)
# insert_ingredient("Cumin", 1, "tsp.", calories=8, total_fat=0.5, sodium=0.8, total_carbohydrate=0.9, total_sugars=0, protein=0.4)
# insert_ingredient("Nutmeg", 1, "tsp.", calories=12, total_fat=0.8, sodium=0.9, total_carbohydrate=1.1, total_sugars=0, protein=0.1)
# insert_ingredient("Ginger", 1, "tsp.", calories=2, total_fat=0, sodium=0.3, total_carbohydrate=0.4, total_sugars=0, protein=0)
# insert_ingredient("Yogurt", 1, "cup(s)", calories=154, total_fat=8, sodium=113, total_carbohydrate=11, total_sugars=11, protein=9)
# insert_ingredient("Tofu", 1, "oz", calories=47, total_fat=2.7, sodium=7, total_carbohydrate=1.2, total_sugars=0.2, protein=5.1)
# insert_ingredient("Mushroom", 1, "cup(s)", calories=15, total_fat=0.2, sodium=4, total_carbohydrate=2.3, total_sugars=1.4, protein=2.2)
# insert_ingredient("Corn", 1, "cup(s)", calories=132, total_fat=1.6, sodium=15, total_carbohydrate=30, total_sugars=6.8, protein=5)
# insert_ingredient("Green Beans", 1, "cup(s)", calories=31, total_fat=0.2, sodium=6, total_carbohydrate=7, total_sugars=3.4, protein=2)
# insert_ingredient("Apple", 1, "piece(s)", calories=95, total_fat=0.3, sodium=2, total_carbohydrate=25, total_sugars=19, protein=0.5)
# insert_ingredient("Banana", 1, "piece(s)", calories=105, total_fat=0.4, sodium=1, total_carbohydrate=27, total_sugars=14, protein=1.3)
# insert_ingredient("Orange", 1, "piece(s)", calories=62, total_fat=0.2, sodium=0, total_carbohydrate=15.4, total_sugars=12.2, protein=1.2)
# insert_ingredient("Strawberry", 1, "cup(s)", calories=49, total_fat=0.5, sodium=2, total_carbohydrate=11.7, total_sugars=7.4, protein=1)
# insert_ingredient("Blueberry", 1, "cup(s)", calories=84, total_fat=0.5, sodium=1, total_carbohydrate=21, total_sugars=14.7, protein=1.1)
# insert_ingredient("Eggplant", 1, "piece(s)", calories=20, total_fat=0.1, sodium=2, total_carbohydrate=4.8, total_sugars=2.4, protein=0.8)
# insert_ingredient("Cauliflower", 1, "cup(s)", calories=27, total_fat=0.3, sodium=32, total_carbohydrate=5.3, total_sugars=2, protein=2.1)


# add_to_pantry("Olive Oil", 50)
# add_to_pantry("Pancetta", 16)
# add_to_pantry("Garlic", 20)
# add_to_pantry("Eggs", 10)
# add_to_pantry("Parmesan Cheese", 100)
# add_to_pantry("Spaghetti", 8)

# https://www.simplyrecipes.com/recipes/spaghetti_alla_carbonara/
# add_recipe("Spaghetti Carbonara", 
#            """
#            1. Heat the pasta water
#            2. Sauté the pancetta or bacon and garlic
#            3. Beat the eggs and half of the cheese
#            4. Cook the pasta
#            5. Toss the pasta with pancetta or bacon
#            6. Add the beaten egg mixture
#            """,
#            [("Olive Oil", 1, "tbsp."), ("Pancetta", 0.5, "lb"), ("Garlic", 2, "piece(s)"), ("Eggs", 4, "piece(s)"), ("Spaghetti", 1, "lb")],
#            meal_type="Lunch",
#            servings=5,
#            prep_time=10,
#            cook_time=15
#            )

# add_recipe("Fried Eggs", 
#            """
#            1. Put olive oil in pan
#            2. Fry the egg
#            """,
#            [("Olive Oil", 1, "tbsp."), ("Eggs", 2, "piece(s)")],
#            meal_type="Breakfast",
#            servings=1,
#            prep_time=0,
#            cook_time=5
#            )

# recipes = filter_recipes(ingredients=["olive oil"], ingredients_available=True, prep_time=(0, 12), meal_type="breakfast")
# for recipe in recipes:
#     print(dict(recipe["recipe"]))

# print(get_expired())

# print(get_ingredient("Garlic"))