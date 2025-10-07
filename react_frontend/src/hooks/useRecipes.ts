//hooks/useRecipes.ts

import { useState, useEffect } from 'react';
import { Recipe, FilterSettings } from '../types';
import { fetchRecipesByIngredients } from '../api/recipeService';

export const useRecipes = (ingredients: string[], filters: FilterSettings) => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRecipes = async () => {
      if (ingredients.length === 0) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Pass filters directly to the API service
        const data = await fetchRecipesByIngredients(ingredients, {
          caloriesMin: filters.caloriesMin,
          caloriesMax: filters.caloriesMax,
          mealTypes: filters.mealTypes
        });
        
        setRecipes(data);
      } catch (err) {
        setError('Failed to load recipes');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadRecipes();
  }, [ingredients, filters]);

  return { recipes, loading, error };
};
