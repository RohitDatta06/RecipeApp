import React from 'react';
import { Recipe } from '../../types';
import './RecipeCard.css';

interface RecipeCardProps {
  recipe?: Recipe;
  isLoading?: boolean;
}

const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, isLoading }) => {
  if (isLoading) {
    return (
      <div className="recipe-card loading">
        <div className="recipe-placeholder">
          <div className="loading-pulse"></div>
        </div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="recipe-card empty">
        <div className="recipe-placeholder">
          <p>No recipe available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recipe-card">
      <div className="recipe-info">
        <h3>{recipe.name}</h3>
        <div className="recipe-meta">
          {recipe.meal_type && <span>{recipe.meal_type}</span>}
          {recipe.prep_time && <span>Prep: {recipe.prep_time} min</span>}
          {recipe.cook_time && <span>Cook: {recipe.cook_time} min</span>}
          {recipe.servings && <span>{recipe.servings} servings</span>}
        </div>
        <div className="recipe-ingredients">
          <h4>Ingredients:</h4>
          <ul>
            {recipe.ingredients.map((ing, idx) => (
              <li key={idx}>{ing.quantity} {ing.unit_of_measurement} {ing.ingredient_name}</li>
            ))}
          </ul>
        </div>
  
        <div className="recipe-instructions">
          <h4>Instructions:</h4>
          {recipe.instructions.split('\n').map((step, idx) =>
            step.trim() ? <p key={idx}><strong>Step {idx + 1}:</strong> {step.trim()}</p> : null
          )}
        </div>
      </div>
    </div>
  );
};

export default RecipeCard;
