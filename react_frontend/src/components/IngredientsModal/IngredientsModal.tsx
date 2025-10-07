import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import './IngredientsModal.css';

const IngredientsModal: React.FC = () => {
  const { 
    ingredients, 
    addIngredient, 
    removeIngredient, 
    clearIngredients, 
    showIngredientsModal, 
    setShowIngredientsModal 
  } = useAppContext();
  
  const [newIngredient, setNewIngredient] = useState('');

  const handleAddIngredient = () => {
    if (newIngredient.trim()) {
      addIngredient(newIngredient.trim());
      setNewIngredient('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddIngredient();
    }
  };

  const handleSubmit = () => {
    if (ingredients.length > 0) {
      setShowIngredientsModal(false);
    }
  };

  if (!showIngredientsModal) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>What ingredients do you have?</h2>
        <p>Add your available ingredients to find matching recipes</p>
        
        <div className="input-container">
          <input
            type="text"
            value={newIngredient}
            onChange={(e) => setNewIngredient(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type an ingredient..."
          />
          <button onClick={handleAddIngredient}>Add</button>
        </div>
        
        <div className="ingredients-list">
          {ingredients.map((ingredient, index) => (
            <div key={index} className="ingredient-pill">
              {ingredient}
              <button onClick={() => removeIngredient(ingredient)}>×</button>
            </div>
          ))}
        </div>
        
        <div className="modal-actions">
          <button 
            onClick={clearIngredients} 
            className="secondary-button"
            disabled={ingredients.length === 0}
          >
            Clear All
          </button>
          <button 
            onClick={handleSubmit} 
            className="primary-button"
            disabled={ingredients.length === 0}
          >
            Find Recipes
          </button>
        </div>
      </div>
    </div>
  );
};

export default IngredientsModal;