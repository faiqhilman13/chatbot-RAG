import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import tnbLogo from '../assets/tnb-logo-plain.svg';
import tnbIcon from '../assets/tnb-icon.svg';
import { useTheme } from '../utils/ThemeContext';

// Import icons (we would typically use a library like react-icons)
const HomeIcon = () => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" /></svg>;
const SummarizeIcon = () => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>;
const VisualizeIcon = () => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>;
const ExtractIcon = () => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>;
const FAQIcon = () => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" /></svg>;
const ChevronIcon = ({ isOpen }) => <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={`w-6 h-6 transition-transform ${isOpen ? '' : 'rotate-180'}`}><path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" /></svg>;

const navItems = [
  { path: '/', name: 'Home', icon: <HomeIcon /> },
  { path: '/summarization', name: 'Summarization Bot', icon: <SummarizeIcon /> },
  { path: '/visualization', name: 'Visualization Bot', icon: <VisualizeIcon /> },
  { path: '/extraction', name: 'Extraction Bot', icon: <ExtractIcon /> },
  { path: '/faq', name: 'FAQ', icon: <FAQIcon /> },
];

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const { darkMode } = useTheme();

  return (
    <div className="h-full bg-white dark:bg-dark-bg-secondary border-r border-gray-200 dark:border-dark-border shadow-lg flex flex-col transition-colors duration-200">
      {/* TNB Logo and Brand */}
      <div className="p-4 flex items-center justify-between border-b border-gray-200 dark:border-dark-border">
        <div className="flex items-center overflow-hidden">
          {isOpen ? (
            <img src={tnbLogo} alt="TNB Logo" className="h-10" />
          ) : (
            <img src={tnbIcon} alt="TNB Logo" className="h-8 w-8 mx-auto" />
          )}
        </div>
        <button onClick={toggleSidebar} className="text-gray-500 dark:text-dark-text-secondary hover:text-tnb-red transition-colors">
          <ChevronIcon isOpen={isOpen} />
        </button>
      </div>
      
      {/* Navigation Links */}
      <nav className="flex-1 pt-4">
        <ul>
          {navItems.map((item) => (
            <li key={item.path} className="mb-1">
              <NavLink
                to={item.path}
                className={({ isActive }) => `
                  flex items-center px-4 py-3 text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-tnb-red text-white' 
                    : 'text-gray-700 dark:text-dark-text-primary hover:bg-gray-100 dark:hover:bg-dark-border'}
                  ${!isOpen && 'justify-center'}
                `}
              >
                <span className="min-w-[24px]">{item.icon}</span>
                {isOpen && <span className="ml-3">{item.name}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-dark-border text-center text-xs text-gray-500 dark:text-dark-text-secondary">
        {isOpen ? 'TNB Internal Use Only • 2023' : ''}
      </div>
    </div>
  );
};

export default Sidebar; 