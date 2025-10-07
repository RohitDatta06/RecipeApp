import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { MealType } from '../../types';
import './FilterControls.css';

const FilterControls: React.FC = () => {
  const { filters, updateFilters, resetFilters } = useAppContext();
  const [showFilters, setShowFilters] = useState(false);
  const handleMealTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateFilters({ mealTypes: [e.target.value as MealType] });
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
              <label>
                Min: <span>{filters.caloriesMin}</span>
              </label>
              <input 
                type="range" 
                min="0" 
                max="2000" 
                value={filters.caloriesMin}
                onChange={(e) => updateFilters({ caloriesMin: Number(e.target.value) })}
              />              
              <label>
                Max: <span>{filters.caloriesMax}</span>
              </label>
              <input 
                type="range" 
                min={filters.caloriesMin} 
                max="2000" 
                value={filters.caloriesMax}
                onChange={(e) => updateFilters({ caloriesMax: Number(e.target.value) })}
              />
            </div>
          </div>
          
          <div className="filter-section">
            <h5>Meal Type</h5>
            <select 
              className="meal-type-dropdown" 
              value={filters.mealTypes[0]}
              onChange={handleMealTypeChange}
            >
              <option value="">None</option>
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
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
