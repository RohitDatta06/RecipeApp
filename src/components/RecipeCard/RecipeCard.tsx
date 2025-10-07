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
      <div className="recipe-image">
        {/* Placeholder image - you could replace this with actual images later */}
        <div className="recipe-placeholder-image">
          <span>{recipe.title.charAt(0)}</span>
        </div>
      </div>
      <div className="recipe-info">
        <h3>{recipe.title}</h3>
        <div className="recipe-meta">
          <span>{recipe.calories} cal</span>
          <span>{recipe.mealType}</span>
          {recipe.preparationTime && (
            <span>Prep: {recipe.preparationTime} min</span>
          )}
        </div>
        <div className="recipe-ingredients-preview">
          <p>{recipe.ingredients.slice(0, 3).join(', ')}
            {recipe.ingredients.length > 3 ? '...' : ''}
          </p>
        </div>
      </div>
    </div>
  );
};

export default RecipeCard;
