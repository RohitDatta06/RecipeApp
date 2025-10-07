import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from flask_backend.src.app import app


# Used Github Copilot to generate test cases

@pytest.fixture
def client():
    """Fixture to set up the Flask test client."""
    with app.test_client() as client:
        yield client

def test_add_ingredient(client):
    """Test the add_ingredient endpoint."""
    # Define the payload for the POST request
    payload = {
        "name": "Test Ingredient",
        "serving_size": 1,
        "unit_of_measurement": "tbsp.",
        "calories": 10,
        "total_fat": 0,
        "sodium": 0,
        "total_carbohydrate": 0,
        "total_sugars": 0,
        "protein": 0,
        "cost": 1.0,
        "shelf_life": 30
    }

    # Send a POST request to the /api/ingredient_post endpoint
    response = client.post("/api/ingredient_post", json=payload)

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains the success message
    data = response.get_json()
    assert data["message"] == "Ingredient added"
    
def test_add_ingredient_to_pantry(client):
    """Test the add_ingredient_to_pantry endpoint."""
    # Define the payload for the POST request
    payload = {
        "ingredient_name": "Test Ingredient",
        "quantity": 5,
        "purchase_date": 1681929600,
        "expiry_date": 1682534400
    }

    # Send a POST request to the /api/pantry_post endpoint
    response = client.post("/api/pantry_post", json=payload)

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains the success message
    data = response.get_json()
    assert data["message"] == "Ingredient added to pantry"
    
    
def test_add_recipe(client):
    """Test the add_recipe endpoint."""
    # Define the payload for the POST request
    payload = {
        "recipe_name": "Test Carbonara",
        "instructions": """
            1. Heat the pasta water.
            2. Sauté the pancetta or bacon and garlic.
            3. Beat the eggs and half of the cheese.
            4. Cook the pasta.
            5. Toss the pasta with pancetta or bacon.
            6. Add the beaten egg mixture.
        """,
        "ingredients": [
            ("Olive Oil", 2, "tbsp."),
            ("Garlic", 3, "pieces"),
            ("Eggs", 4, "pieces")
        ],
        "meal_type": "Dinner",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4
    }

    # Send a POST request to the /api/recipe_post endpoint
    response = client.post("/api/recipe_post", json=payload)

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains the success message
    data = response.get_json()
    assert data["message"] == "Recipe added"
    
def test_expiring(client):
    """Test the get_expiring endpoint."""
    # Send a GET request to the /api/expiring endpoint
    response = client.get("/api/expiring/10")

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains a list of expiring items
    data = response.get_json()
    assert isinstance(data, list)    
    
def test_expired(client):
    """Test the get_expired endpoint."""
    # Send a GET request to the /api/expired endpoint
    response = client.get("/api/expired")

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains a list of expired items
    data = response.get_json()
    assert isinstance(data, list)
    
def test_generate_recipe(client):
    """Test the generate_recipe endpoint."""
    # Define the payload for the POST request
    payload = {
        "user_question": ["pasta", "eggs", "cheese"],
        "user_preference": "Italian"
    }

    # Send a POST request to the /api/generate_recipe endpoint
    response = client.post("/api/generate_recipe", json=payload)

    # Assert the response status code is 200 (success)
    assert response.status_code == 200

    # Assert the response JSON contains a recipe
    data = response.get_json()
    assert isinstance(data, dict)
    assert data["message"] == "Recipe generated and saved"
