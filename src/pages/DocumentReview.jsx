import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const DocumentReview = () => {
  const [primaryFile, setPrimaryFile] = useState(null);
  const [referenceFiles, setReferenceFiles] = useState([]);
  const [reviewSettings, setReviewSettings] = useState({
    checkFormat: true,
    checkContent: true,
    checkCompliance: true,
    highlightChanges: true
  });
  const [processing, setProcessing] = useState(false);
  const [reviewResult, setReviewResult] = useState(null);
  
  const handlePrimaryUpload = (files) => {
    if (files.length > 0) {
      setPrimaryFile(files[0]);
    }
  };
  
  const handleReferenceUpload = (files) => {
    setReferenceFiles(files);
  };
  
  const handleSettingChange = (setting) => {
    setReviewSettings({
      ...reviewSettings,
      [setting]: !reviewSettings[setting]
    });
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!primaryFile || referenceFiles.length === 0) {
      alert('Please upload both primary and reference documents');
      return;
    }
    
    // In a real application, this would be an API call to the backend
    setProcessing(true);
    
    // Simulate API call
    setTimeout(() => {
      // Sample review results
      const sampleResults = {
        summary: {
          matchScore: 87,
          formatConsistency: 92,
          contentAccuracy: 85,
          complianceScore: 90
        },
        issues: [
          {
            type: 'content',
            severity: 'high',
            location: 'Section 3.2, Paragraph 2',
            description: 'Missing key clause regarding data protection requirements',
            recommendation: 'Add standard clause from template section 3.2.1'
          },
          {
            type: 'format',
            severity: 'medium',
            location: 'Section 5.1, Bullet Points',
            description: 'Inconsistent formatting compared to reference document',
            recommendation: 'Update bullet point style to match reference document'
          },
          {
            type: 'compliance',
            severity: 'low',
            location: 'Appendix A',
            description: 'Referenced regulation is outdated (2018 version)',
            recommendation: 'Update to 2023 version of the regulation'
          }
        ],
        changes: {
          additions: 12,
          deletions: 5,
          modifications: 8
        },
        sections: [
          {
            name: 'Introduction',
            matchScore: 95,
            issues: 0
          },
          {
            name: 'Terms and Conditions',
            matchScore: 78,
            issues: 2
          },
          {
            name: 'Legal Requirements',
            matchScore: 86,
            issues: 1
          },
          {
            name: 'Technical Specifications',
            matchScore: 92,
            issues: 0
          },
          {
            name: 'Appendices',
            matchScore: 88,
            issues: 1
          }
        ]
      };
      
      setReviewResult(sampleResults);
      setProcessing(false);
    }, 3000);
  };
  
  // Helper function to get severity color
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      case 'medium':
        return 'text-amber-600 bg-amber-50 dark:bg-amber-900/20';
      case 'low':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-800/20';
    }
  };
  
  // Helper function to get issue type icon
  const getIssueTypeIcon = (type) => {
    switch (type) {
      case 'content':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'format':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
          </svg>
        );
      case 'compliance':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
        );
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Document Review Agent
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Compare documents against reference materials to identify discrepancies, format issues, and 
          ensure compliance. Ideal for contract review, document standardization, and regulatory compliance.
        </p>
      </div>
      
      <div className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-sm p-6 mb-8 border border-gray-200 dark:border-dark-border">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Primary Document
            </label>
            <FileUpload 
              onUpload={handlePrimaryUpload} 
              allowedTypes={['.pdf', '.docx', '.doc', '.txt']} 
              multiple={false}
            />
            {primaryFile && (
              <div className="mt-2 text-sm text-gray-600 dark:text-dark-text-secondary">
                Uploaded: {primaryFile.name}
              </div>
            )}
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Reference Document(s)
            </label>
            <FileUpload 
              onUpload={handleReferenceUpload} 
              allowedTypes={['.pdf', '.docx', '.doc', '.txt']} 
              multiple={true}
            />
            {referenceFiles.length > 0 && (
              <div className="mt-2 text-sm text-gray-600 dark:text-dark-text-secondary">
                Uploaded: {referenceFiles.length} {referenceFiles.length === 1 ? 'file' : 'files'}
              </div>
            )}
          </div>
          
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-2">
              Review Settings
            </h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  className="rounded text-tnb-blue focus:ring-tnb-blue h-4 w-4" 
                  checked={reviewSettings.checkFormat}
                  onChange={() => handleSettingChange('checkFormat')}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                  Check formatting consistency
                </span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  className="rounded text-tnb-blue focus:ring-tnb-blue h-4 w-4" 
                  checked={reviewSettings.checkContent}
                  onChange={() => handleSettingChange('checkContent')}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                  Verify content accuracy and completeness
                </span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  className="rounded text-tnb-blue focus:ring-tnb-blue h-4 w-4" 
                  checked={reviewSettings.checkCompliance}
                  onChange={() => handleSettingChange('checkCompliance')}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                  Check regulatory compliance
                </span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  className="rounded text-tnb-blue focus:ring-tnb-blue h-4 w-4" 
                  checked={reviewSettings.highlightChanges}
                  onChange={() => handleSettingChange('highlightChanges')}
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-dark-text-secondary">
                  Highlight changes and differences
                </span>
              </label>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={processing || !primaryFile || referenceFiles.length === 0}
            >
              {processing ? 'Reviewing Document...' : 'Review Document'}
            </button>
          </div>
        </form>
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Analyzing documents and finding discrepancies...</p>
        </div>
      )}
      
      {reviewResult && !processing && (
        <div className="space-y-6 my-8">
          <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-4 py-3 border-b border-gray-200 dark:border-dark-border">
              <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
                Document Review Summary
              </h2>
            </div>
            
            {/* Summary Scores */}
            <div className="p-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-tnb-blue">{reviewResult.summary.matchScore}%</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Overall Match</div>
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-tnb-blue">{reviewResult.summary.formatConsistency}%</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Format Consistency</div>
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-tnb-blue">{reviewResult.summary.contentAccuracy}%</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Content Accuracy</div>
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary rounded-lg p-3 text-center">
                  <div className="text-2xl font-bold text-tnb-blue">{reviewResult.summary.complianceScore}%</div>
                  <div className="text-sm text-gray-600 dark:text-dark-text-secondary">Compliance Score</div>
                </div>
              </div>
              
              {/* Changes Summary */}
              <div className="flex flex-wrap gap-4 mb-6">
                <div className="px-3 py-1 rounded-full bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 text-sm">
                  {reviewResult.changes.additions} Additions
                </div>
                <div className="px-3 py-1 rounded-full bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
                  {reviewResult.changes.deletions} Deletions
                </div>
                <div className="px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-sm">
                  {reviewResult.changes.modifications} Modifications
                </div>
              </div>
              
              {/* Section Scores */}
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 dark:text-dark-text-primary mb-3">Section Analysis</h3>
                <div className="space-y-2">
                  {reviewResult.sections.map((section, index) => (
                    <div key={index} className="flex items-center">
                      <div className="w-1/3 text-sm text-gray-700 dark:text-dark-text-secondary">{section.name}</div>
                      <div className="w-1/3">
                        <div className="w-full bg-gray-200 dark:bg-dark-bg-primary rounded-full h-2.5">
                          <div 
                            className="bg-tnb-blue h-2.5 rounded-full" 
                            style={{ width: `${section.matchScore}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="w-1/6 text-right text-sm text-gray-600 dark:text-dark-text-secondary">
                        {section.matchScore}%
                      </div>
                      <div className="w-1/6 text-right">
                        {section.issues > 0 ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300">
                            {section.issues} {section.issues === 1 ? 'issue' : 'issues'}
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300">
                            No issues
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Issues List */}
              <div>
                <h3 className="font-medium text-gray-900 dark:text-dark-text-primary mb-3">Identified Issues</h3>
                <div className="divide-y divide-gray-200 dark:divide-dark-border">
                  {reviewResult.issues.map((issue, index) => (
                    <div key={index} className="py-3">
                      <div className="flex items-center mb-2">
                        <div className="mr-2">
                          {getIssueTypeIcon(issue.type)}
                        </div>
                        <span className="font-medium text-gray-900 dark:text-dark-text-primary">
                          {issue.location}
                        </span>
                        <span className={`ml-2 px-2 py-0.5 rounded-full text-xs ${getSeverityColor(issue.severity)}`}>
                          {issue.severity.charAt(0).toUpperCase() + issue.severity.slice(1)} Severity
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-dark-text-secondary mb-1">
                        {issue.description}
                      </p>
                      <p className="text-sm text-tnb-blue dark:text-tnb-blue/80">
                        <strong>Recommendation:</strong> {issue.recommendation}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would download a detailed report
                alert('Export functionality would be implemented here');
              }}
            >
              Export Detailed Report
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                // In a real app, this would highlight the changes directly in the document
                alert('Open document with highlights functionality would be implemented here');
              }}
            >
              View Marked Document
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Document Review Agent
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload the document you want to review.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload one or more reference documents (templates, previous versions, etc.).</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Select the review settings based on your needs.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the results to identify discrepancies and areas for improvement.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Export a detailed report or view the document with highlighted changes.</li>
        </ol>
      </div>
    </div>
  );
};

export default DocumentReview; 