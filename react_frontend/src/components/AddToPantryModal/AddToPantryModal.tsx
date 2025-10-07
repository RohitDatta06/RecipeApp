// components/AddToPantryModal.tsx
import React, { useState } from 'react';
import { addIngredientToPantry } from '../../api/recipeService';
import './AddToPantryModal.css';

interface Props {
  onClose: () => void;
}

const AddToPantryModal: React.FC<Props> = ({ onClose }) => {
  const [ingredient_name, setName] = useState('');
  const [quantity, setQuantity] = useState('');
  const [purchase_date, setPurchaseDate] = useState('');
  const [expiry_date, setExpiryDate] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addIngredientToPantry({
        ingredient_name,
        quantity: parseFloat(quantity),
        purchase_date: Math.floor(new Date(purchase_date).getTime() / 1000),
        expiry_date: Math.floor(new Date(expiry_date).getTime() / 1000),
      });
      alert('Ingredient added!');
      onClose();
    } catch (err) {
      alert('Failed to add');
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Add Ingredient to Pantry</h3>
        <form onSubmit={handleSubmit}>
          <input type="text" placeholder="Name" value={ingredient_name} onChange={e => setName(e.target.value)} required />
          <input type="number" placeholder="Quantity" value={quantity} onChange={e => setQuantity(e.target.value)} required />
          <input type="date" value={purchase_date} onChange={e => setPurchaseDate(e.target.value)} />
          <input type="date" value={expiry_date} onChange={e => setExpiryDate(e.target.value)} />
          <button type="submit">Add</button>
          <button type="button" onClick={onClose}>Cancel</button>
        </form>
      </div>
    </div>
  );
};

export default AddToPantryModal;
