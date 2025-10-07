//types/index.ts


export interface Recipe {
  title: string;
  ingredients: string[];
  instructions: string;
  calories: number;
  mealType: MealType;
  preparationTime?: number;
  cookTime?: number;
  servings?: number;
  category?: string;
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