import { Link } from 'react-router-dom';

const agentCards = [
  {
    title: 'SQL Agent',
    description: 'Convert natural language questions to SQL queries and get answers from your database.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
      </svg>
    ),
    link: '/sql-agent'
  },
  {
    title: 'Report Generation',
    description: 'Generate professional Excel and PowerPoint reports from documents and custom prompts.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    link: '/report-generation'
  },
  {
    title: 'Document Review',
    description: 'Compare documents against reference materials to identify discrepancies and ensure compliance.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    link: '/document-review'
  },
  {
    title: 'Classification Agent',
    description: 'Classify data based on reference documents and custom rulesets for automated decision-making.',
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-tnb-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
      </svg>
    ),
    link: '/classification'
  }
];

const HomePage = () => {
  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero Section */}
      <section className="text-center py-8 mb-12">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-dark-text-primary mb-4">
          Welcome to the AI Agent Platform
        </h1>
        <p className="text-lg text-gray-600 dark:text-dark-text-secondary max-w-3xl mx-auto">
          Access powerful AI agents to query databases, generate reports, review documents, and classify data for your business needs.
        </p>
      </section>
      
      {/* Agent Cards Section */}
      <section className="grid md:grid-cols-2 gap-8 mb-12">
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
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Secure Data Processing</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">All data is processed securely and never leaves your organization's systems.</p>
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
              <p className="text-gray-600 dark:text-dark-text-secondary">Get insights within seconds, even from complex queries and large documents.</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="rounded-full bg-tnb-red p-2 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-1">Multiple Input Types</h3>
              <p className="text-gray-600 dark:text-dark-text-secondary">Process natural language queries, documents, spreadsheets, and more.</p>
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
              <p className="text-gray-600 dark:text-dark-text-secondary">Choose the right AI agent for your specific business needs.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage; 