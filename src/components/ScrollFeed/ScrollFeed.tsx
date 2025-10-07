

import React, { useState, useRef, useEffect } from 'react';
import RecipeCard from '../RecipeCard';
import { Recipe } from '../../types';
import './ScrollFeed.css';

interface ScrollFeedProps {
  recipes: Recipe[];
  loading: boolean;
}

const ScrollFeed: React.FC<ScrollFeedProps> = ({ recipes, loading }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const feedRef = useRef<HTMLDivElement>(null);
  
  // just for show
  const displayRecipes = recipes.length > 0 ? recipes : Array(5).fill(null);
  
  const handleScroll = () => {
    if (!feedRef.current) return;
    
    const scrollTop = feedRef.current.scrollTop;
    const itemHeight = feedRef.current.clientHeight;
    const index = Math.round(scrollTop / itemHeight);
    
    if (index !== currentIndex) {
      setCurrentIndex(index);
    }
  };
  

  useEffect(() => {
    const feed = feedRef.current;
    if (!feed) return;
    
    feed.addEventListener('scroll', handleScroll);
    
    return () => {
      feed.removeEventListener('scroll', handleScroll);
    };
  }, []);
  
  const handleTouchStart = (e: React.TouchEvent) => {
    const touchStartY = e.touches[0].clientY;
    
    const handleTouchMove = (e: TouchEvent) => {
      const touchY = e.touches[0].clientY;
      const diff = touchStartY - touchY;
      
      if (Math.abs(diff) > 50) {
        if (diff > 0 && currentIndex < displayRecipes.length - 1) {
          setCurrentIndex(currentIndex + 1);
        } else if (diff < 0 && currentIndex > 0) {
          setCurrentIndex(currentIndex - 1);
        }
        
        if (feedRef.current) {
          feedRef.current.scrollTo({
            top: currentIndex * feedRef.current.clientHeight,
            behavior: 'smooth'
          });
        }
        
        window.removeEventListener('touchmove', handleTouchMove);
      }
    };
    
    window.addEventListener('touchmove', handleTouchMove);
    
    const handleTouchEnd = () => {
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
    
    window.addEventListener('touchend', handleTouchEnd);
  };
  
  return (
    <div 
      className="scroll-feed" 
      ref={feedRef}
      onTouchStart={handleTouchStart}
    >
      {displayRecipes.map((recipe, index) => (
        <div key={index} className="feed-item">
          <RecipeCard recipe={recipe} isLoading={loading} />
        </div>
      ))}
    </div>
  );
};

export default ScrollFeed;