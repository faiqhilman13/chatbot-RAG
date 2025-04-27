import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const Classification = () => {
  const [files, setFiles] = useState([]);
  const [rulesets, setRulesets] = useState([
    { id: 1, name: 'Default Ruleset', isDefault: true },
    { id: 2, name: 'HR Documents', isDefault: false },
    { id: 3, name: 'Financial Reports', isDefault: false },
    { id: 4, name: 'Legal Contracts', isDefault: false }
  ]);
  const [selectedRuleset, setSelectedRuleset] = useState(1);
  const [customRules, setCustomRules] = useState('');
  const [processing, setProcessing] = useState(false);
  const [classificationResults, setClassificationResults] = useState(null);
  
  const handleUpload = (uploadedFiles) => {
    setFiles(uploadedFiles);
  };
  
  const handleRulesetChange = (e) => {
    setSelectedRuleset(parseInt(e.target.value));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      alert('Please upload files to classify');
      return;
    }
    
    // In a real application, this would be an API call to the backend
    setProcessing(true);
    
    // Simulate API call
    setTimeout(() => {
      // Sample classification results
      const sampleResults = {
        totalDocuments: files.length,
        categories: {
          'Financial': files.length > 0 ? Math.ceil(files.length * 0.4) : 0,
          'Legal': files.length > 0 ? Math.ceil(files.length * 0.25) : 0,
          'HR': files.length > 0 ? Math.floor(files.length * 0.2) : 0,
          'Technical': files.length > 0 ? Math.floor(files.length * 0.15) : 0
        },
        confidenceScore: 92,
        files: files.map((file, index) => {
          const categories = ['Financial', 'Legal', 'HR', 'Technical'];
          const randomCategory = categories[Math.floor(Math.random() * categories.length)];
          const confidenceScores = {
            'Financial': Math.random() * 30 + 10,
            'Legal': Math.random() * 30 + 10,
            'HR': Math.random() * 30 + 10,
            'Technical': Math.random() * 30 + 10
          };
          
          // Ensure the assigned category has the highest score
          confidenceScores[randomCategory] = Math.random() * 40 + 60;
          
          return {
            name: file.name,
            size: file.size,
            category: randomCategory,
            confidence: confidenceScores[randomCategory],
            metadata: {
              sensitivityLevel: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
              containsPII: Math.random() > 0.7,
              retentionPeriod: ['1 year', '3 years', '5 years', '7 years'][Math.floor(Math.random() * 4)]
            },
            allScores: confidenceScores
          };
        })
      };
      
      setClassificationResults(sampleResults);
      setProcessing(false);
    }, 2000);
  };
  
  // Helper function to format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  // Helper function to get confidence level color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-blue-600';
    if (confidence >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  // Helper function to get category color
  const getCategoryColor = (category) => {
    switch (category) {
      case 'Financial':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'Legal':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'HR':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400';
      case 'Technical':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Classification Agent
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Automatically classify documents and data based on reference materials and custom rulesets.
          Perfect for organizing documents, applying policies, and automated workflow routing.
        </p>
      </div>
      
      <div className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-sm p-6 mb-8 border border-gray-200 dark:border-dark-border">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Upload Files to Classify
            </label>
            <FileUpload 
              onUpload={handleUpload} 
              allowedTypes={['.pdf', '.docx', '.xlsx', '.csv', '.txt', '.pptx', '.jpg', '.png']} 
              multiple={true}
            />
            {files.length > 0 && (
              <div className="mt-2 text-sm text-gray-600 dark:text-dark-text-secondary">
                {files.length} {files.length === 1 ? 'file' : 'files'} uploaded
              </div>
            )}
          </div>
          
          <div className="mb-6">
            <label htmlFor="ruleset" className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Select Classification Ruleset
            </label>
            <select
              id="ruleset"
              className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
              value={selectedRuleset}
              onChange={handleRulesetChange}
            >
              {rulesets.map(ruleset => (
                <option key={ruleset.id} value={ruleset.id}>
                  {ruleset.name} {ruleset.isDefault ? '(Default)' : ''}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-6">
            <label htmlFor="custom-rules" className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Custom Rules (Optional)
            </label>
            <textarea
              id="custom-rules"
              rows="4"
              className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
              placeholder="Example: Classify as 'HR' if contains 'employee review', 'performance evaluation', or 'personnel'"
              value={customRules}
              onChange={(e) => setCustomRules(e.target.value)}
            ></textarea>
            <p className="text-xs text-gray-500 dark:text-dark-text-secondary mt-1">
              Enter custom classification rules using natural language. These will be combined with the selected ruleset.
            </p>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={processing || files.length === 0}
            >
              {processing ? 'Classifying...' : 'Classify Documents'}
            </button>
          </div>
        </form>
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Analyzing and classifying your documents...</p>
        </div>
      )}
      
      {classificationResults && !processing && (
        <div className="space-y-6 my-8">
          <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-4 py-3 border-b border-gray-200 dark:border-dark-border">
              <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
                Classification Results
              </h2>
            </div>
            
            <div className="p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary">{classificationResults.totalDocuments}</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Total Documents</div>
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-tnb-blue">{classificationResults.confidenceScore}%</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Avg. Confidence</div>
                </div>
                <div className="col-span-2 bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3">
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">Categories Distribution</div>
                  <div className="flex items-center">
                    {Object.entries(classificationResults.categories).map(([category, count], index) => {
                      const colors = [
                        'bg-green-500 dark:bg-green-600',
                        'bg-blue-500 dark:bg-blue-600',
                        'bg-purple-500 dark:bg-purple-600',
                        'bg-orange-500 dark:bg-orange-600'
                      ];
                      const percentage = Math.round((count / classificationResults.totalDocuments) * 100);
                      
                      return (
                        <div 
                          key={category}
                          className={`h-4 ${colors[index % colors.length]}`}
                          style={{ width: `${percentage}%` }}
                          title={`${category}: ${count} (${percentage}%)`}
                        >
                        </div>
                      );
                    })}
                  </div>
                  <div className="flex justify-between mt-1 text-xs text-gray-500 dark:text-dark-text-secondary">
                    {Object.entries(classificationResults.categories).map(([category, count]) => (
                      <div key={category}>
                        {category}: {count}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 dark:text-dark-text-primary mb-3">Document Classification</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                    <thead className="bg-gray-50 dark:bg-dark-bg-primary">
                      <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          File
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Category
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Confidence
                        </th>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider">
                          Metadata
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-dark-bg-secondary divide-y divide-gray-200 dark:divide-dark-border">
                      {classificationResults.files.map((file, index) => (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white dark:bg-dark-bg-secondary' : 'bg-gray-50 dark:bg-dark-bg-primary/50'}>
                          <td className="px-4 py-3 text-sm">
                            <div className="font-medium text-gray-900 dark:text-dark-text-primary">{file.name}</div>
                            <div className="text-xs text-gray-500 dark:text-dark-text-secondary">{formatFileSize(file.size)}</div>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(file.category)}`}>
                              {file.category}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <div className={`font-medium ${getConfidenceColor(file.confidence)}`}>
                              {Math.round(file.confidence)}%
                            </div>
                            <div className="mt-1 w-full bg-gray-200 dark:bg-dark-bg-primary rounded-full h-1.5">
                              <div 
                                className={`h-1.5 rounded-full ${file.confidence >= 90 ? 'bg-green-500' : file.confidence >= 70 ? 'bg-blue-500' : file.confidence >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} 
                                style={{ width: `${file.confidence}%` }}
                              ></div>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <div>
                              <span className="text-xs font-medium text-gray-700 dark:text-dark-text-secondary">Sensitivity: </span>
                              <span className="text-xs text-gray-600 dark:text-dark-text-secondary">{file.metadata.sensitivityLevel}</span>
                            </div>
                            <div>
                              <span className="text-xs font-medium text-gray-700 dark:text-dark-text-secondary">Contains PII: </span>
                              <span className="text-xs text-gray-600 dark:text-dark-text-secondary">{file.metadata.containsPII ? 'Yes' : 'No'}</span>
                            </div>
                            <div>
                              <span className="text-xs font-medium text-gray-700 dark:text-dark-text-secondary">Retention: </span>
                              <span className="text-xs text-gray-600 dark:text-dark-text-secondary">{file.metadata.retentionPeriod}</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would export the classification results
                alert('Export functionality would be implemented here');
              }}
            >
              Export Results
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                // In a real app, this would apply the classifications to the documents
                alert('Apply Classifications functionality would be implemented here');
              }}
            >
              Apply Classifications
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Classification Agent
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload the documents you want to classify.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Select an existing classification ruleset based on your organization's requirements.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Add any custom classification rules if needed for specific document types.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the classification results and make adjustments if necessary.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Apply the classifications to automate document workflows, retention policies, or access controls.</li>
        </ol>
      </div>
    </div>
  );
};

export default Classification; 