//Sidebar/Sidebar.tsx


import React from 'react';
import { useAppContext } from '../../context/AppContext';
import FilterControls from '../FilterControls/FilterControls';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const { ingredients, setShowIngredientsModal } = useAppContext();

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
      
      <div className="sidebar-footer">
        <p>Swipe up for more recipes</p>
      </div>
    </div>
  );
};

export default Sidebar;