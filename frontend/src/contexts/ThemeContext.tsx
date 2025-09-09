import React, { createContext, useContext, useState, useEffect, useMemo, useCallback } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>('light');

  useEffect(() => {
    // We read the theme from the data-theme attribute on the html element
    // This is set by the inline script in index.html
    const currentTheme = document.documentElement.getAttribute('data-theme') as Theme | null;
    if (currentTheme) {
      setThemeState(currentTheme);
    }
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    try {
      window.localStorage.setItem('theme', newTheme);
      document.documentElement.setAttribute('data-theme', newTheme);
      setThemeState(newTheme);
    } catch (e) {
      console.warn('Failed to set theme in localStorage:', e);
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  }, [theme, setTheme]);

  const value = useMemo(() => ({ theme, setTheme, toggleTheme }), [theme, setTheme, toggleTheme]);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};