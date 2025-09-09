import { useState, useEffect } from 'react';

export type Theme = 'dark' | 'light';

const getInitialTheme = (): Theme => {
  if (typeof window === 'undefined') return 'dark';
  
  try {
    // Check localStorage first
    const stored = localStorage.getItem('cyber-theme') as Theme;
    if (stored && ['dark', 'light'].includes(stored)) {
      return stored;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
  } catch (error) {
    console.warn('Failed to get initial theme:', error);
  }
  
  return 'dark';
};

export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>('dark');
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize theme on client side only
  useEffect(() => {
    const initialTheme = getInitialTheme();
    setTheme(initialTheme);
    setIsInitialized(true);
  }, []);

  useEffect(() => {
    if (!isInitialized) return;
    
    const root = document.documentElement;
    
    // Apply theme to document with transition
    root.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    root.setAttribute('data-theme', theme);
    
    // Add theme class for better CSS targeting
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(`theme-${theme}`);
    
    // Store in localStorage
    try {
      localStorage.setItem('cyber-theme', theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme === 'dark' ? '#0B1020' : '#FDFCF7');
    }
    
    // Clean up transition after theme change
    const cleanup = setTimeout(() => {
      root.style.transition = '';
    }, 300);
    
    return () => clearTimeout(cleanup);
  }, [theme, isInitialized]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const setThemeMode = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  return {
    theme,
    toggleTheme,
    setTheme: setThemeMode,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };
};