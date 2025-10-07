import requests
import json
from dotenv import load_dotenv
import os
from . import recipe_interface
import re
import sqlite3
load_dotenv()
ARLIAI_API_KEY = os.getenv("ARLIAI_API_KEY")

def get_pantry_summary():
    """
    Retrieves a summary of the user's pantry ingredients from the database.
    Returns:
        str: A formatted string summarizing the total quantities of each ingredient in the pantry.
    """
    # Connect to the database and retrieve pantry summary
    conn = sqlite3.connect('flask_backend/pantry.db')
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    
    try:
        c.execute("""
            SELECT
                p.ingredient_name,
                SUM(p.quantity) AS total_quantity,
                i.unit_of_measurement
            FROM pantry AS p
            JOIN ingredients AS i
                ON p.ingredient_name = i.name
            GROUP BY p.ingredient_name
        """)
        rows = c.fetchall()
    except sqlite3.Error as error:
        print("Failed to retrieve pantry summary:", error)
        conn.close()
        return []
    
    conn.close()
    ingred_summary = ""
    for row in rows:
        name, total_qty, unit = row
        ingred = f"{name}: {total_qty} {unit} total in pantry\n"
        ingred_summary += ingred
    return ingred_summary


def parse_recipe_json(text):
    """
    Extracts and parses a JSON object from a text block that contains
    a JSON-formatted recipe enclosed in triple backticks (e.g., ```json ... ```).

    Args:
        text (str): A string containing a JSON block inside triple backticks.

    Returns:
        dict: The parsed JSON object representing the recipe.

    Raises:
        ValueError: If no JSON block is found or if the JSON is invalid.
    """
    match1 = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    match2 = re.search(r'(\{.*?\})', text, re.DOTALL)
    if not match1 and not match2:
        raise ValueError("No JSON block found in the input text.")
    
    json_str = match1.group(1) if match1 else match2.group(1)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def parse_ingredient_string(ingredient_str):
    """
    Parses a string describing an ingredient into a structured format.

    Example:
        "12 oz spaghetti" -> ("spaghetti", 12, "oz")

    Args:
        ingredient_str (str): The ingredient string to parse.

    Returns:
        tuple: A tuple of the form (ingredient name, quantity, unit).
               Defaults to (ingredient_str, 1, "-") if parsing fails.
    """
    # parts = ingredient_str.split()
    # if len(parts) < 2:
    #     return (ingredient_str, 1, "-")
    
    # try:
    #     quantity = float(parts[0])
    #     unit = parts[1]
    #     name = " ".join(parts[2:])
    #     return (name, quantity, unit)
    # except ValueError:
    #     return (ingredient_str, 1, "-")
    
    if len(ingredient_str) == 2:
        name, qty = ingredient_str
        return (name, float(qty), "piece(s)")
    
    name, qty, unit = ingredient_str
    return (name, float(qty), unit)


def add_parsed_recipe_from_text(text):
    """
    Extracts a recipe from a markdown-style JSON block, parses the relevant fields,
    and adds it to the recipe interface.

    Args:
        text (str): A string containing a markdown-formatted recipe in JSON,
                    enclosed in triple backticks and optionally labeled as 'json'.

    Side Effects:
        Calls `recipe_interface.add_recipe()` to store the parsed recipe.

    Fields Extracted:
        - title (str): Name of the recipe.
        - instructions (list of str): Step-by-step instructions.
        - ingredients (list of str): List of raw ingredient strings.
        - prep_time (int or str): Preparation time in minutes.
        - cook_time (int or str): Cooking time in minutes.

    Notes:
        Time fields may be given as strings (e.g., "30 minutes") or integers (e.g., 30).
        Ingredient strings are parsed into (name, quantity, unit) tuples.
    """
    recipe_data = parse_recipe_json(text)
    
    name = recipe_data.get("title", "Untitled Recipe")
    instructions = "\n".join(recipe_data.get("instructions", []))
    ingredients_raw = recipe_data.get("ingredients", [])
    prep_time = recipe_data.get("prep_time", -1)
    cook_time = recipe_data.get("cook_time", -1)
    meal_type = recipe_data.get("meal_type", None)

    def parse_time(t):
        if isinstance(t, str):
            match = re.search(r'\d+', t)
            return int(match.group()) if match else -1
        return t if isinstance(t, int) else -1

    prep_time = parse_time(prep_time)
    cook_time = parse_time(cook_time)
    
    ingredients = [parse_ingredient_string(i) for i in ingredients_raw]
    
    recipe_interface.add_recipe(name, instructions, ingredients, prep_time=prep_time, meal_type=meal_type, cook_time=cook_time)

def get_recipe_from_user(user_question, user_preference=None):
    """
    Generates a recipe based on the user's pantry ingredients and optional preferences.

    Args:
        user_question (str): A summary of the ingredients available in the user's pantry.
        user_preference (str, optional): User's preferred style or cuisine for the recipe.
            Defaults to None.
    
    Returns:
        str: A JSON-formatted string containing the recipe title, ingredients, and instructions.
    """
  
    # Get the list of ingredient names from the database
    conn = sqlite3.connect('flask_backend/pantry.db')
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    ingredient_names = []
    units = []
    recipe_names = []
    try:
        c.execute("SELECT name FROM ingredients")
        ingredient_names = [row["name"].lower() for row in c.fetchall()]
        c.execute("SELECT unit FROM units")
        units = [row["unit"] for row in c.fetchall()]
        c.execute("SELECT name FROM recipes")
        recipe_names = [row["name"].lower() for row in c.fetchall()]

    except sqlite3.Error as error:
        print(f"Failed to get ingredient names/units: ", error)
    finally:
        conn.close()
        
    print(ingredient_names)
    print(recipe_names)
    print(units)
        
    system_prompt = f"""
    You are a helpful assistant that generates detailed recipes based on a provided list of ingredients. 
    Please adhere to the following guidelines:
    1. Prioritise using mostly just the ingredients from the user's pantry.
       If needed, you can also use the following ingredients list: {', '.join(ingredient_names)}. USE NOTHING ELSE.
    2. Include a list of the required ingredients for the recipe. You MUST use EXACTLY the SAME name and SAME spelling as provided.
    3. Provide clear, step-by-step cooking instructions.
    4. Estimate approximate cooking/preparation times.
    5. Generate a recipe NOT included in this list: {', '.join(recipe_names)}.

    Combine them in a way that results in a balanced, flavorful dish, and detail the recipe thoroughly.

    Finally, please return  the recipe title, ingredients, and instructions in JSON format, with ABSOLUTELY NO backslashes or comments.
        
    The JSON should look like this:
    For ingredient, copy LETTER FOR LETTER from the following keys: {', '.join(ingredient_names)}.
    For quantity, you MUST ONLY use an integer or decimal numbers, NO fractions, NO units and NO strings.
    For unit, copy LETTER FOR LETTER one of the following keys: {', '.join(units)}. If there is no appropriate unit, default to using "piece(s)".
    {{
        "title": "Recipe Title",
        "ingredients": [
            ["Ingredient 1", "quantity", "unit"],
            ["Ingredient 2", "quantity", "unit"],
            ...
        ],
        "instructions": [
            "Step 1",
            "Step 2",
            ...
        ],
        "meal_type": (breakfast, lunch, dinner or snack)
        "prep_time": "X minutes",
        "cook_time": "Y minutes"
    }}

    Only include the ingredients under ONE LIST. Make sure any information about cooking time is included as a bullet point under instructions. 
    You MUST use the format provided above.
    """

    if user_preference:
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": "Please make the recipe in this style: " + str(user_preference) + "\n" +
             "Here is a summary of the ingredients in my pantry:\n" + str(user_question)}
        ]
    else:
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": "Here is a summary of the ingredients in my pantry:\n" + str(user_question)}
        ]

    payload = {
        "model": "Mistral-Nemo-12B-Instruct-2407",
        "messages": messages,
        "repetition_penalty": 1.1,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 1024,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ARLIAI_API_KEY}"
    }

    url = "https://api.arliai.com/v1/chat/completions"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        try:
            answer = data["choices"][0]["message"]["content"]
            return answer
        except (KeyError, IndexError):
            print("Error: Unexpected response format:", data)
    else:
        print(f"Error: Received status code {response.status_code}\n{response.text}")


### Example usage
if __name__ == "__main__":
    # user_question = get_pantry_summary()
    user_question = "eggs"
    user_preference = "Italian"
    text = get_recipe_from_user(user_question, user_preference)
    print(text)
    add_parsed_recipe_from_text(text)
