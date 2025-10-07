//api/recipeService.ts

import { Recipe } from '../types';

//adjust this according to the backend setup
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
    
    ingredients.forEach(ingredient => {
      params.append('ingredients', ingredient);
    });

    if (filters?.caloriesMin !== undefined) {
      params.append('calories_min', filters.caloriesMin.toString());
    }
    
    if (filters?.caloriesMax !== undefined) {
      params.append('calories_max', filters.caloriesMax.toString());
    }
    
    if (filters?.mealTypes && filters.mealTypes.length > 0) {
      filters.mealTypes.forEach(type => {
        params.append('meal_type', type);
      });
    }
  
    const response = await fetch(`${API_BASE_URL}/recipes?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.recipes;
  } catch (error) {
    console.error('Error fetching recipes:', error);
    throw error;
  }
};