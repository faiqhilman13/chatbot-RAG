import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const SummarizationBot = () => {
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [processing, setProcessing] = useState(false);
  
  const handleUpload = (uploadedFiles) => {
    setFiles(uploadedFiles);
    // In a real application, you would send these files to a backend or API
    if (uploadedFiles.length > 0) {
      // Simulate API call
      setProcessing(true);
      setTimeout(() => {
        setProcessing(false);
        setSummary({
          title: "Document Summary",
          content: "This is a simulated summary of the uploaded document. In a real application, this would contain the AI-generated summary highlighting the key points and insights from your document. This summary would be tailored to the specific content of your uploaded files and would help you quickly understand the main ideas without reading the entire document.",
          keyPoints: [
            "Key point 1 extracted from the document",
            "Key point 2 with important information",
            "Key point 3 highlighting critical insights",
            "Key point 4 with noteworthy data"
          ]
        });
      }, 2000);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Summarization Bot
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Upload lengthy documents and receive condensed summaries highlighting key information. 
          Perfect for quickly understanding reports, contracts, and research papers.
        </p>
      </div>
      
      <div className="mb-8">
        <FileUpload onUpload={handleUpload} />
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Processing your document...</p>
        </div>
      )}
      
      {summary && !processing && (
        <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm p-6 my-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary mb-4">
            {summary.title}
          </h2>
          
          <div className="prose max-w-none mb-6">
            <p className="text-gray-800 dark:text-dark-text-primary">{summary.content}</p>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-2">
              Key Points
            </h3>
            <ul className="list-disc pl-5 space-y-1">
              {summary.keyPoints.map((point, index) => (
                <li key={index} className="text-gray-600 dark:text-dark-text-secondary">
                  {point}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would download a PDF or text file
                alert('Download functionality would be implemented here');
              }}
            >
              Download Summary
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                setSummary(null);
                setFiles([]);
              }}
            >
              New Summary
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Summarization Bot
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload your document using the file uploader above.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Wait a few moments while our AI processes your content.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the generated summary and key points.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Download the summary for sharing or future reference.</li>
        </ol>
      </div>
    </div>
  );
};

export default SummarizationBot; 