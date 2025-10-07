import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { MealType } from '../../types';
import './FilterControls.css';

const FilterControls: React.FC = () => {
  const { filters, updateFilters, resetFilters } = useAppContext();
  const [showFilters, setShowFilters] = useState(false);
  
  const handleMealTypeToggle = (mealType: MealType) => {
    const currentMealTypes = [...filters.mealTypes];
    
    if (currentMealTypes.includes(mealType)) {
      updateFilters({ 
        mealTypes: currentMealTypes.filter(type => type !== mealType) 
      });
    } else {
      updateFilters({ 
        mealTypes: [...currentMealTypes, mealType] 
      });
    }
  };

  return (
    <div className="filter-controls">
      <button 
        className="filter-toggle-button"
        onClick={() => setShowFilters(!showFilters)}
      >
        {showFilters ? 'Hide Filters' : 'Show Filters'}
      </button>
      
      {showFilters && (
        <div className="filters-container">
          <h4>Filters</h4>
          
          <div className="filter-section">
            <h5>Calories</h5>
            <div className="calorie-range">
              <input 
                type="range" 
                min="0" 
                max="2000" 
                value={filters.caloriesMin}
                onChange={(e) => updateFilters({ caloriesMin: Number(e.target.value) })}
              />
              <div className="range-values">
                <span>{filters.caloriesMin}</span>
                <span>to</span>
                <input 
                  type="range" 
                  min={filters.caloriesMin} 
                  max="2000" 
                  value={filters.caloriesMax}
                  onChange={(e) => updateFilters({ caloriesMax: Number(e.target.value) })}
                />
                <span>{filters.caloriesMax}</span>
              </div>
            </div>
          </div>
          
          <div className="filter-section">
            <h5>Meal Type</h5>
            <div className="meal-type-options">
              {(['breakfast', 'lunch', 'dinner', 'snack'] as MealType[]).map(type => (
                <label key={type} className="meal-type-option">
                  <input 
                    type="checkbox" 
                    checked={filters.mealTypes.includes(type)}
                    onChange={() => handleMealTypeToggle(type)}
                  />
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </label>
              ))}
            </div>
          </div>
          
          <button className="reset-filters-button" onClick={resetFilters}>
            Reset Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default FilterControls;