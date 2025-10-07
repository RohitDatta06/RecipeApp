//types/index.ts


export interface Recipe {
  name: string;  // (was title before)
  instructions: string;
  meal_type?: MealType;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  calories?: number; 
  ingredients: Ingredient[];  // proper list, not just strings
}

export interface Ingredient {
  ingredient_name: string;
  quantity: number;
  unit_of_measurement: string;
}

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export interface FilterSettings {
  caloriesMin: number;
  caloriesMax: number;
  mealTypes: MealType[];
}

export interface AppContextType {
  ingredients: string[];
  addIngredient: (ingredient: string) => void;
  removeIngredient: (ingredient: string) => void;
  clearIngredients: () => void;
  showIngredientsModal: boolean;
  setShowIngredientsModal: (show: boolean) => void;
  isLoading: boolean;
  filters: FilterSettings;
  updateFilters: (newFilters: Partial<FilterSettings>) => void;
  resetFilters: () => void;
}
