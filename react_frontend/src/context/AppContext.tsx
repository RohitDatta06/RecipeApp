//context/AppContext.tsx


import React, { createContext, useState, useContext, ReactNode } from 'react';
import { AppContextType, FilterSettings, MealType } from '../types';

const AppContext = createContext<AppContextType | undefined>(undefined);

const DEFAULT_FILTERS: FilterSettings = {
  caloriesMin: 0,
  caloriesMax: 1000,
  mealTypes: []
};

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [showIngredientsModal, setShowIngredientsModal] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [filters, setFilters] = useState<FilterSettings>(DEFAULT_FILTERS);

  const addIngredient = (ingredient: string) => {
    if (!ingredients.includes(ingredient)) {
      setIngredients([...ingredients, ingredient]);
    }
  };

  const removeIngredient = (ingredient: string) => {
    setIngredients(ingredients.filter(item => item !== ingredient));
  };

  const clearIngredients = () => {
    setIngredients([]);
  };

  const updateFilters = (newFilters: Partial<FilterSettings>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFilters(DEFAULT_FILTERS);
  };

  return (
    <AppContext.Provider
      value={{
        ingredients,
        addIngredient,
        removeIngredient,
        clearIngredients,
        showIngredientsModal,
        setShowIngredientsModal,
        isLoading,
        filters,
        updateFilters,
        resetFilters
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};