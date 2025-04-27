import { Link } from 'react-router-dom';

const agentCards = [
  {
    title: 'Summarization Bot',
    description: 'Upload lengthy documents and receive condensed summaries highlighting key information.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
    link: '/summarization'
  },
  {
    title: 'Visualization Bot',
    description: 'Transform raw data into insightful charts and visualizations for better understanding.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
      </svg>
    ),
    link: '/visualization'
  },
  {
    title: 'Extraction Bot',
    description: 'Automatically extract specific data fields and information from complex documents.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
    link: '/extraction'
  }
];

const HomePage = () => {
  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero Section */}
      <section className="text-center py-8 mb-12">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-dark-text-primary mb-4">
          Welcome to the TNB Document AI Platform
        </h1>
        <p className="text-lg text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto">
          Upload your business documents and let our specialized AI agents help you extract insights,
          visualize data, and summarize important information.
        </p>
      </section>
      
      {/* Agent Cards Section */}
      <section className="grid md:grid-cols-3 gap-8 mb-12">
        {agentCards.map((card, index) => (
          <Link 
            key={index}
            to={card.link}
            className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-100 dark:border-dark-border"
          >
            <div className="mb-4">
              {card.icon}
            </div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary mb-2">
              {card.title}
            </h2>
            <p className="text-gray-600 dark:text-dark-text-secondary mb-4">
              {card.description}
            </p>
            <div className="text-tnb-blue font-medium flex items-center">
              Get Started
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
          </Link>
        ))}
      </section>
      
      {/* Features Section */}
      <section className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-8 mb-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-6">
          Platform Features
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="flex items-start">
            <div className="rounded-full bg-tnb-red p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Secure Document Handling</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">All documents are processed securely and never leave TNB's systems.</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="rounded-full bg-tnb-blue p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Fast Processing</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">Get insights within seconds, even from large and complex documents.</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="rounded-full bg-tnb-red p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Multiple Document Types</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">Process PDFs, Word documents, Excel spreadsheets, and more.</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="rounded-full bg-tnb-blue p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Specialized Agents</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">Choose the right AI agent for your specific document needs.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 