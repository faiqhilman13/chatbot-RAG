import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const ExtractionBot = () => {
  const [files, setFiles] = useState([]);
  const [extraction, setExtraction] = useState(null);
  const [processing, setProcessing] = useState(false);
  
  const handleUpload = (uploadedFiles) => {
    setFiles(uploadedFiles);
    
    // In a real application, you would send these files to a backend or API
    if (uploadedFiles.length > 0) {
      // Simulate API call
      setProcessing(true);
      setTimeout(() => {
        setProcessing(false);
        // Sample extraction data (this would come from backend in a real app)
        setExtraction({
          documentType: "Invoice",
          extractedData: [
            { field: "Invoice Number", value: "INV-2023-10-42", confidence: 0.98 },
            { field: "Date", value: "2023-10-15", confidence: 0.99 },
            { field: "Amount", value: "$1,250.00", confidence: 0.97 },
            { field: "Vendor", value: "Acme Supplies Inc.", confidence: 0.95 },
            { field: "Payment Terms", value: "Net 30", confidence: 0.90 },
            { field: "Due Date", value: "2023-11-14", confidence: 0.92 },
            { field: "Tax Amount", value: "$87.50", confidence: 0.94 },
            { field: "Purchase Order", value: "PO-7825", confidence: 0.89 }
          ],
          tables: [
            {
              name: "Line Items",
              headers: ["Item", "Quantity", "Unit Price", "Total"],
              rows: [
                ["Office Supplies", "10", "$25.00", "$250.00"],
                ["Printer Paper", "5", "$12.00", "$60.00"],
                ["Desk Chair", "1", "$275.00", "$275.00"],
                ["Monitor Stand", "2", "$45.00", "$90.00"]
              ]
            }
          ]
        });
      }, 2000);
    }
  };
  
  // Helper function to display confidence level
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.95) return "Very High";
    if (confidence >= 0.85) return "High";
    if (confidence >= 0.70) return "Medium";
    return "Low";
  };
  
  // Helper function to get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.95) return "text-green-600";
    if (confidence >= 0.85) return "text-blue-600";
    if (confidence >= 0.70) return "text-yellow-600";
    return "text-red-600";
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Extraction Bot
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Extract structured data from documents like invoices, receipts, and forms.
          Perfect for automating data entry and building searchable databases from document archives.
        </p>
      </div>
      
      <div className="mb-8">
        <FileUpload 
          onUpload={handleUpload} 
          allowedTypes={['.pdf', '.jpg', '.jpeg', '.png', '.tif']} 
        />
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Processing your document...</p>
        </div>
      )}
      
      {extraction && !processing && (
        <div className="space-y-8 my-8">
          <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-4 py-3 border-b border-gray-200 dark:border-dark-border">
              <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
                Extracted Data: {extraction.documentType}
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200 dark:divide-dark-border">
              {extraction.extractedData.map((item, index) => (
                <div key={index} className="px-4 py-3 flex justify-between items-center">
                  <div className="w-1/3 font-medium text-gray-700 dark:text-dark-text-secondary">{item.field}</div>
                  <div className="w-1/3 text-gray-900 dark:text-dark-text-primary">{item.value}</div>
                  <div className={`w-1/3 text-right text-sm ${getConfidenceColor(item.confidence)}`}>
                    {getConfidenceLabel(item.confidence)} Confidence
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {extraction.tables.map((table, tableIndex) => (
            <div key={tableIndex} className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
              <div className="bg-gray-50 dark:bg-dark-bg-primary px-4 py-3 border-b border-gray-200 dark:border-dark-border">
                <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
                  {table.name}
                </h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                  <thead className="bg-gray-50 dark:bg-dark-bg-primary">
                    <tr>
                      {table.headers.map((header, headerIndex) => (
                        <th 
                          key={headerIndex}
                          className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider"
                        >
                          {header}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-dark-bg-secondary divide-y divide-gray-200 dark:divide-dark-border">
                    {table.rows.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-4 py-3 text-sm text-gray-900 dark:text-dark-text-primary">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
          
          <div className="flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would export data to CSV or Excel
                alert('Export functionality would be implemented here');
              }}
            >
              Export Data
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                setExtraction(null);
                setFiles([]);
              }}
            >
              New Extraction
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Extraction Bot
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload your document (PDF, image, scanned form) using the file uploader.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Wait while our AI identifies and extracts the data fields.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the extracted information and confidence levels.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Export the data to your preferred format (CSV, Excel, etc.).</li>
        </ol>
      </div>
    </div>
  );
};

export default ExtractionBot; 