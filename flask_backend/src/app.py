from flask import Flask, request, jsonify
from flask_cors import CORS
from . import recipe_interface
from . import llm_interface
import sys

app = Flask(__name__)
CORS(app)

# Convert URL safe-string to normal string:
# Replace _ with spaces,
# Make all lowercase
def normalized_string(str):
    return str.replace("_", " ").lower()

# add ingredient type
@app.route('/api/ingredient_post', methods=['POST'])
def add_ingredient():
    if request.method == 'POST':
        data = request.get_json()
        
        name = data.get("name")
        serving_size = data.get("serving_size")
        unit_of_measurement = data.get("unit_of_measurement")
        calories = data.get("calories")
        total_fat = data.get("total_fat")
        sodium = data.get("sodium")
        total_carbohydrate = data.get("total_carbohydrate")
        total_sugars = data.get("total_sugars")
        protein = data.get("protein")
        cost = data.get("cost")
        shelf_life = data.get("shelf_life")
        
        success = recipe_interface.insert_ingredient(name, serving_size, unit_of_measurement, calories=calories, 
                                                     total_fat=total_fat, sodium=sodium, total_carbohydrate=total_carbohydrate, 
                                                     total_sugars=total_sugars, protein=protein, cost=cost, shelf_life=shelf_life)
        if success:
            return (jsonify({"message": "Ingredient added"}), 200)
        else:
            return (jsonify({"error": "Failed to add ingredient"}), 500)
    else:
        return jsonify({"error": "Invalid request method"}), 405
    
# add ingredient to pantry
@app.route('/api/pantry_post', methods=['POST'])
def add_ingredient_to_pantry():
    if request.method == 'POST':
        data = request.get_json()
        
        ingredient_name = data.get("ingredient_name")
        quantity = data.get("quantity")
        purchase_date = data.get("purchase_date")
        expiry_date = data.get("expiry_date")
        
        success = recipe_interface.add_to_pantry(ingredient_name, quantity, purchase_date=purchase_date, expiry_date=expiry_date)
        
        if success:
                return (jsonify({"message": "Ingredient added to pantry"}), 200)
        else:
            return (jsonify({"error": "Failed to add ingredient to pantry"}), 500)
    else:
        return jsonify({"error": "Invalid request method"}), 405

# add recipes
@app.route('/api/recipe_post', methods=['POST'])
def add_recipe():
    if request.method == 'POST':
        data = request.get_json()
        
        recipe_name = data.get("recipe_name")
        instructions = data.get("instructions")
        ingredients = data.get("ingredients", [])
        meal_type = data.get("meal_type")
        prep_time = data.get("prep_time")
        cook_time = data.get("cook_time")
        servings = data.get("servings")
        
        success = recipe_interface.add_recipe(recipe_name, instructions, ingredients, meal_type=meal_type, 
                                              prep_time=prep_time, cook_time=cook_time, servings=servings)
        
        if success:
                return (jsonify({"message": "Recipe added"}), 200)
        else:
            return (jsonify({"error": "Failed to add recipe"}), 500)
    else:
        return jsonify({"error": "Invalid request method"}), 405

# get ingredient type from pantry by:
@app.route("/api/ingredients/<ingredient_name>")
def get_ingredient(ingredient_name):
    try:
        ingredient = recipe_interface.get_ingredient(normalized_string(ingredient_name))
        return jsonify(ingredient)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# get recipe by name (use normalized recipe name)
@app.route("/api/recipes/<recipe_name>")
def get_recipe(recipe_name):
    try:
        recipe = recipe_interface.get_recipe(normalized_string(recipe_name))
        return jsonify(recipe), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# query recipes by preptime, required ingredients and whether or not ingredients are available in pantry
# e.g. /api/recipes/?ingredients=garlic,olive_oil&prep_time=0,20&available=true&meal_type=lunch
@app.route("/api/recipes/")
def get_filtered_recipes():
    try:
        ingredients = request.args.get("ingredients")
        ingredients = [normalized_string(ingredient) for ingredient in ingredients.split(',')] if ingredients else None
        meal_type = request.args.get("meal_type")
        meal_type = normalized_string(meal_type) if meal_type else None
        prep_time = request.args.get("prep_time")
        prep_time = prep_time.split(',') if prep_time else None
        cook_time = request.args.get("cook_time")
        cook_time = cook_time.split(',') if cook_time else None
        available = request.args.get("available") == "true"
        
        filtered_recipes = recipe_interface.filter_recipes(prep_time=prep_time, cook_time=cook_time, ingredients=ingredients, meal_type=meal_type, ingredients_available=available)
        
        return jsonify(filtered_recipes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Generate recipes using LLM
@app.route("/api/generate_recipe", methods=['POST'])
def generate_recipe():
    try:
        data = request.get_json()
        ingredients = data.get("ingredients", [])
        preference = data.get("preference", None)
        user_question = ", ".join(ingredients)
        # LLM call
        llm_response = llm_interface.get_recipe_from_user(user_question, preference)
        print(llm_response)
        llm_interface.add_parsed_recipe_from_text(llm_response)
        return jsonify({"message": "Recipe generated and saved"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

# get expiring ingredients
@app.route("/api/expiring/<days>")
def get_expiring(days):
    try:
        ingredients = recipe_interface.get_expiring(int(days))
        return jsonify(ingredients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# get expired ingredients
@app.route("/api/expired")
def get_expired():
    try:
        ingredients = recipe_interface.get_expired()
        return jsonify(ingredients), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)