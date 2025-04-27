import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

const MainLayout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-dark-bg-primary transition-colors duration-200">
      {/* Sidebar */}
      <motion.div 
        className="fixed h-full z-20"
        initial={{ width: 250 }}
        animate={{ width: isSidebarOpen ? 250 : 64 }}
        transition={{ duration: 0.15 }}
      >
        <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      </motion.div>
      
      {/* Main Content */}
      <div className="flex flex-col flex-1">
        <Header />
        <motion.main 
          className="flex-1 overflow-y-auto p-6 bg-white dark:bg-dark-bg-primary transition-colors duration-200"
          initial={{ marginLeft: 250 }}
          animate={{ marginLeft: isSidebarOpen ? 250 : 64 }}
          transition={{ duration: 0.15 }}
        >
          <Outlet />
        </motion.main>
      </div>
    </div>
  );
};

export default MainLayout; 