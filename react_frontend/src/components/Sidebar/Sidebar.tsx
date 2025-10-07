import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import FilterControls from '../FilterControls/FilterControls';
import './Sidebar.css';
import { generateRecipe } from '../../api/recipeService';
import AddToPantryModal from '../AddToPantryModal';
import AddRecipeModal from '../AddRecipeModal';

const Sidebar: React.FC = () => {
  const { ingredients, setShowIngredientsModal, filters } = useAppContext();
  const [showPantryModal, setShowPantryModal] = useState(false);
  const [showRecipeModal, setShowRecipeModal] = useState(false);
  const handleGenerate = async () => {
    if (ingredients.length === 0) {
      alert('Please select ingredients first!');
      return;
    }
    try {
      await generateRecipe(ingredients, filters.mealTypes[0]); 
      window.location.reload();
    } catch (error) {
      alert('Failed to generate recipe');
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>cs222</h3>
      </div>
      <div className="sidebar-section">
        <h4>Your Ingredients</h4>
        {ingredients.length > 0 ? (
          <div className="ingredients-list-sidebar">
            {ingredients.map((ingredient, index) => (
              <div key={index} className="ingredient-item">
                {ingredient}
              </div>
            ))}
          </div>
        ) : (
          <p>No ingredients added yet</p>
        )}
        <button
          className="edit-ingredients-button"
          onClick={() => setShowIngredientsModal(true)}
        >
          Edit Ingredients
        </button>
      </div>
      <div className="sidebar-section">
        <FilterControls />
      </div>

      <div className="sidebar-section">
        <button onClick={handleGenerate}>✨ Generate Recipe</button>
        <button onClick={() => setShowPantryModal(true)}>➕ Add to Pantry</button>
        <button onClick={() => setShowRecipeModal(true)}>📄 Add Manual Recipe</button>
      </div>

      <div className="sidebar-footer">
        <p>Swipe up for more recipes</p>
      </div>
      {showPantryModal && <AddToPantryModal onClose={() => setShowPantryModal(false)} />}
      {showRecipeModal && <AddRecipeModal onClose={() => setShowRecipeModal(false)} />}
    </div>
  );
};

export default Sidebar;
