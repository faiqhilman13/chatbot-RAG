import React from 'react';
import { useTheme } from '../utils/ThemeContext';
import tnbLogo from '../assets/tnb-logo-plain.svg';
import { Link } from 'react-router-dom';

const Header = () => {
  // In a real application, this would be fetched from an auth provider
  const user = {
    name: 'John Doe',
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
    role: 'Energy Analyst'
  };

  const { darkMode, toggleDarkMode } = useTheme();

  return (
    <header className="bg-white dark:bg-dark-bg-secondary border-b border-gray-200 dark:border-dark-border h-16 flex items-center justify-between px-6 sticky top-0 z-10 transition-colors duration-200">
      <div className="flex items-center">
        <Link to="/" className="flex items-center">
          <img src={tnbLogo} alt="TNB Logo" className="h-9 hidden sm:block" />
        </Link>
      </div>
      
      <div className="flex items-center space-x-4">
        {/* Dark Mode Toggle */}
        <button 
          onClick={toggleDarkMode}
          className="text-gray-500 dark:text-dark-text-secondary hover:text-tnb-blue dark:hover:text-tnb-blue p-1 rounded-full transition-colors"
          aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {darkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {/* Notifications */}
        <button className="text-gray-500 dark:text-dark-text-secondary hover:text-tnb-blue dark:hover:text-tnb-blue p-1 rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        </button>

        {/* User Profile */}
        <div className="flex items-center space-x-3">
          <div className="hidden md:block text-right">
            <p className="text-sm font-medium text-gray-800 dark:text-dark-text-primary">{user.name}</p>
            <p className="text-xs text-gray-500 dark:text-dark-text-secondary">{user.role}</p>
          </div>
          <div className="h-10 w-10 rounded-full overflow-hidden border-2 border-tnb-blue">
            <img 
              src={user.avatar} 
              alt={user.name} 
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 