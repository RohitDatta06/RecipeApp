//api/recipeService.ts

import { Recipe } from '../types/index.js';

const API_BASE_URL = 'http://localhost:5000/api';

export const fetchRecipesByIngredients = async (
  ingredients: string[],
  filters?: {
    caloriesMin?: number;
    caloriesMax?: number;
    mealTypes?: string[];
  }
): Promise<Recipe[]> => {
  try {
    const params = new URLSearchParams();
    
    if (ingredients.length > 0) {
      params.append('ingredients', ingredients.map(i => i.replace(/\s+/g, '_')).join(','));
    }

    if (filters?.mealTypes && filters.mealTypes.length > 0) {
      params.append('meal_type', filters.mealTypes[0]);
    }
  
    const response = await fetch(`${API_BASE_URL}/recipes/?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    const recipes: Recipe[] = data.map((entry: any) => ({
      name: entry.recipe.name,
      instructions: entry.recipe.instructions,
      meal_type: entry.recipe.meal_type,
      prep_time: entry.recipe.prep_time,
      cook_time: entry.recipe.cook_time,
      servings: entry.recipe.servings,
      calories: entry.recipe.calories,
      ingredients: entry.ingredients,
    }));

    return recipes;
  } catch (error) {
    console.error('Error fetching recipes:', error);
    throw error;
  }
};

export const generateRecipe = async (
  ingredients: string[],
  preference?: string
): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate_recipe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ingredients, preference })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    console.log('Generated recipe:', data.message);
  } catch (error) {
    console.error('Error generating recipe:', error);
    throw error;
  }
};

export const addIngredientToPantry = async (ingredientData: {
  ingredient_name: string;
  quantity: number;
  purchase_date?: number;
  expiry_date?: number;
}) => {
  const res = await fetch(`${API_BASE_URL}/pantry_post`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(ingredientData)
  });
  if (!res.ok) throw new Error("Failed to add ingredient to pantry");
};

export const addManualRecipe = async (recipeData: {
  recipe_name: string;
  instructions: string;
  ingredients: [string, number, string][];
  meal_type: string;
  prep_time: number;
  cook_time: number;
  servings: number;
}) => {
  const res = await fetch(`${API_BASE_URL}/recipe_post`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(recipeData)
  });
  if (!res.ok) throw new Error("Failed to add recipe");
};
