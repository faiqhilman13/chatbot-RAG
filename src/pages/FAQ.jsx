import { useState } from 'react';

const faqItems = [
  {
    question: "What types of documents can I upload?",
    answer: "Our platform supports a wide range of document formats including PDF, Word documents (.doc, .docx), Excel spreadsheets (.xls, .xlsx), CSV files, and various image formats (.jpg, .png, .tif). Each specialized AI agent may have specific format preferences for optimal results."
  },
  {
    question: "Is my data secure?",
    answer: "Yes, all uploaded documents and extracted data remain within TNB's secure infrastructure. Documents are not shared with external services, and all processing happens on our internal servers. Your documents are automatically removed after processing unless you specifically choose to save them."
  },
  {
    question: "How accurate is the data extraction?",
    answer: "Our AI has been trained on thousands of TNB documents and achieves high accuracy rates, typically 95%+ for standard forms and documents. Each extracted field comes with a confidence score so you can verify information with lower confidence levels. The system continues to improve with usage."
  },
  {
    question: "Can I process multiple documents at once?",
    answer: "Yes, you can upload multiple documents simultaneously. The system will process them in sequence and provide results for each. For large batch processing needs (50+ documents), please contact IT Support for optimized handling."
  },
  {
    question: "How do I share the results with colleagues?",
    answer: "Each AI agent offers export capabilities. You can download summaries as PDF or text files, visualizations as image files or interactive dashboards, and extracted data as structured CSV or Excel files. You can then share these through TNB's internal systems."
  },
  {
    question: "What if the AI makes a mistake?",
    answer: "While our AI agents are highly accurate, they may occasionally misinterpret data. Always review the results, particularly for critical business decisions. If you spot an error, use the feedback function to report it - this helps improve the system for future use."
  },
  {
    question: "Who do I contact for technical support?",
    answer: "For technical issues or questions, contact the TNB IT Support Desk at extension 4357 (HELP) or email at itsupport@tnb.internal. Support is available Monday-Friday, 8AM-6PM."
  },
  {
    question: "Can I customize the output format?",
    answer: "Currently, each agent provides standardized output formats designed for TNB's internal systems and workflows. Advanced customization options are planned for future releases. If you have specific formatting needs, please submit a request through the feedback form."
  }
];

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const toggleQuestion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };
  
  const filteredFaqs = searchQuery 
    ? faqItems.filter(item => 
        item.question.toLowerCase().includes(searchQuery.toLowerCase()) || 
        item.answer.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : faqItems;
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Frequently Asked Questions
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Find answers to common questions about the TNB Document AI Platform.
        </p>
      </div>
      
      {/* Search bar */}
      <div className="mb-8">
        <div className="relative">
          <input
            type="text"
            placeholder="Search FAQ..."
            className="w-full px-4 py-3 border border-gray-300 dark:border-dark-border dark:bg-dark-bg-secondary dark:text-dark-text-primary rounded-lg focus:ring-2 focus:ring-tnb-blue focus:border-tnb-blue"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="absolute right-3 top-3 text-gray-400 dark:text-dark-text-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
      
      {/* FAQ accordion */}
      <div className="space-y-4">
        {filteredFaqs.length > 0 ? (
          filteredFaqs.map((item, index) => (
            <div 
              key={index} 
              className="border border-gray-200 dark:border-dark-border rounded-lg overflow-hidden"
            >
              <button
                className="w-full text-left px-6 py-4 flex justify-between items-center focus:outline-none bg-white dark:bg-dark-bg-secondary"
                onClick={() => toggleQuestion(index)}
              >
                <h3 className="font-medium text-gray-900 dark:text-dark-text-primary">{item.question}</h3>
                <span className="text-tnb-blue">
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    className={`h-5 w-5 transition-transform ${openIndex === index ? 'transform rotate-180' : ''}`} 
                    viewBox="0 0 20 20" 
                    fill="currentColor"
                  >
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </span>
              </button>
              
              {openIndex === index && (
                <div className="px-6 py-4 bg-gray-50 dark:bg-dark-bg-primary border-t border-gray-200 dark:border-dark-border">
                  <p className="text-gray-700 dark:text-dark-text-secondary">{item.answer}</p>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-dark-text-secondary">No matching questions found. Try a different search term.</p>
          </div>
        )}
      </div>
      
      {/* Contact section */}
      <div className="mt-12 bg-tnb-blue bg-opacity-5 dark:bg-dark-bg-secondary dark:bg-opacity-100 rounded-lg p-6 border border-transparent dark:border-dark-border">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary mb-3">
          Still have questions?
        </h2>
        <p className="text-gray-600 dark:text-dark-text-secondary mb-4">
          If you couldn't find the answer to your question, feel free to reach out to our support team.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-tnb-blue mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <span className="text-gray-700 dark:text-dark-text-primary">itsupport@tnb.internal</span>
          </div>
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-tnb-red mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span className="text-gray-700 dark:text-dark-text-primary">Extension 4357 (HELP)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQ; 