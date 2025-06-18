import React, { createContext, useState, useContext } from 'react';

// Define page constants
export const PAGES = {
  CHAT: 'chat',
  DOCUMENTS: 'documents',
  UPLOAD: 'upload',
};

// Create context
const PageContext = createContext();

// Create provider component
export const PageProvider = ({ children }) => {
  const [activePage, setActivePage] = useState(PAGES.CHAT);

  return (
    <PageContext.Provider value={{ activePage, setActivePage }}>
      {children}
    </PageContext.Provider>
  );
};

// Custom hook to use the page context
export const usePage = () => {
  const context = useContext(PageContext);
  if (!context) {
    throw new Error('usePage must be used within a PageProvider');
  }
  return context;
}; 