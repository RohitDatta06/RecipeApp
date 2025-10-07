import React, { useState } from 'react';
import { AppProvider, useAppContext } from './context/AppContext';
import IngredientsModal from './components/IngredientsModal';
import ScrollFeed from './components/ScrollFeed';
import Sidebar from './components/Sidebar';
import { useRecipes } from './hooks/useRecipes';
import './App.css';

const AppContent: React.FC = () => {
  const { ingredients, showIngredientsModal, filters } = useAppContext();
  const { recipes, loading } = useRecipes(ingredients, filters);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app">
      <IngredientsModal />
      <div className={`app-content ${showIngredientsModal ? 'blurred' : ''}`}>
        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          ☰
        </button>
        <div className={`sidebar-container ${sidebarOpen ? 'open' : ''}`}>
          <Sidebar />
        </div>
        <div className="feed-container">
          <ScrollFeed recipes={recipes} loading={loading} />
        </div>
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;