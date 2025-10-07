// components/AddRecipeModal.tsx
import React, { useState } from 'react';
import { addManualRecipe } from '../../api/recipeService';
import './AddRecipeModal.css';

interface Props {
  onClose: () => void;
}

const AddRecipeModal: React.FC<Props> = ({ onClose }) => {
  const [recipe_name, setName] = useState('');
  const [instructions, setInstructions] = useState('');
  const [ingredientsRaw, setIngredientsRaw] = useState('');
  const [meal_type, setMealType] = useState('');
  const [prep_time, setPrepTime] = useState('');
  const [cook_time, setCookTime] = useState('');
  const [servings, setServings] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const ingredients: [string, number, string][] = ingredientsRaw.split('\n').map(line => {
      const [ingredient_name, quantity, unit_of_measurement] = line.split(',').map(x => x.trim());
      return [ingredient_name, parseFloat(quantity), unit_of_measurement];
    });

    try {
      await addManualRecipe({
        recipe_name,
        instructions,
        ingredients,
        meal_type,
        prep_time: parseInt(prep_time),
        cook_time: parseInt(cook_time),
        servings: parseInt(servings)
      });
      alert('Recipe added!');
      onClose();
    } catch (err) {
      alert('Failed to add');
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Add Manual Recipe</h3>
        <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Name" value={recipe_name} onChange={e => setName(e.target.value)} required />
          <textarea placeholder="Instructions" value={instructions} onChange={e => setInstructions(e.target.value)} required />
          <textarea
            placeholder="Ingredients (name, quantity, unit)\nOne per line"
            value={ingredientsRaw}
            onChange={e => setIngredientsRaw(e.target.value)}
            required
          />
          <input type="text" placeholder="Meal Type" value={meal_type} onChange={e => setMealType(e.target.value)} required />
          <input type="number" placeholder="Prep Time (min)" value={prep_time} onChange={e => setPrepTime(e.target.value)} required />
          <input type="number" placeholder="Cook Time (min)" value={cook_time} onChange={e => setCookTime(e.target.value)} required />
          <input type="number" placeholder="Servings" value={servings} onChange={e => setServings(e.target.value)} required />
          <button type="submit">Add Recipe</button>
          <button type="button" onClick={onClose}>Cancel</button>
        </form>
      </div>
    </div>
  );
};

export default AddRecipeModal;
