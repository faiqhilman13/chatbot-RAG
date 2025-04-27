import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const ReportGeneration = () => {
  const [files, setFiles] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [reportType, setReportType] = useState('excel');
  const [reportStyle, setReportStyle] = useState('professional');
  const [processing, setProcessing] = useState(false);
  const [reportPreview, setReportPreview] = useState(null);
  
  const handleUpload = (uploadedFiles) => {
    setFiles(uploadedFiles);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (files.length === 0 || !prompt.trim()) {
      alert('Please upload files and provide a report prompt');
      return;
    }
    
    // In a real application, this would be an API call to the backend
    setProcessing(true);
    
    // Simulate API call
    setTimeout(() => {
      // Sample preview data
      const previewData = {
        reportType,
        reportStyle,
        preview: reportType === 'excel' 
          ? 'excel-report-preview.png' 
          : 'powerpoint-report-preview.png',
        sections: [
          {
            title: 'Executive Summary',
            content: 'This report analyzes the financial performance for Q3 2023, showing a 12% increase in revenue compared to the previous quarter. Key growth areas include enterprise sales and subscription services.'
          },
          {
            title: 'Key Performance Indicators',
            charts: ['Revenue Growth by Category', 'Customer Acquisition Cost', 'Customer Lifetime Value']
          },
          {
            title: 'Regional Analysis',
            tables: [
              {
                name: 'Revenue by Region',
                rows: 5,
                columns: 4
              }
            ]
          },
          {
            title: 'Recommendations',
            bullets: [
              'Increase investment in enterprise sales team',
              'Optimize customer onboarding to reduce churn',
              'Expand product offerings in the APAC region'
            ]
          }
        ],
        estimatedPages: reportType === 'excel' ? '3 worksheets' : '12 slides',
        estimatedSize: '4.2 MB'
      };
      
      setReportPreview(previewData);
      setProcessing(false);
    }, 2500);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Report Generation Agent
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Upload documents and let AI generate professional Excel or PowerPoint reports.
          Perfect for financial analysis, sales summaries, or performance reviews.
        </p>
      </div>
      
      <div className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-sm p-6 mb-8 border border-gray-200 dark:border-dark-border">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Upload Documents
            </label>
            <FileUpload 
              onUpload={handleUpload} 
              allowedTypes={['.pdf', '.docx', '.xlsx', '.csv', '.txt', '.pptx']} 
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Report Prompt
            </label>
            <textarea
              id="prompt"
              rows="3"
              className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
              placeholder="Example: Create a quarterly financial report with revenue trends and regional breakdown"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            ></textarea>
            <p className="text-sm text-gray-500 dark:text-dark-text-secondary mt-1">
              Be specific about what information you want to include and how to structure it.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
                Report Type
              </label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input 
                    type="radio" 
                    className="form-radio text-tnb-blue" 
                    name="reportType" 
                    value="excel" 
                    checked={reportType === 'excel'} 
                    onChange={() => setReportType('excel')} 
                  />
                  <span className="ml-2 text-gray-700 dark:text-dark-text-secondary">Excel</span>
                </label>
                <label className="inline-flex items-center">
                  <input 
                    type="radio" 
                    className="form-radio text-tnb-blue" 
                    name="reportType" 
                    value="powerpoint" 
                    checked={reportType === 'powerpoint'} 
                    onChange={() => setReportType('powerpoint')} 
                  />
                  <span className="ml-2 text-gray-700 dark:text-dark-text-secondary">PowerPoint</span>
                </label>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
                Report Style
              </label>
              <select
                className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
                value={reportStyle}
                onChange={(e) => setReportStyle(e.target.value)}
              >
                <option value="professional">Professional</option>
                <option value="creative">Creative</option>
                <option value="minimal">Minimal</option>
                <option value="detailed">Detailed</option>
              </select>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={processing || files.length === 0 || !prompt.trim()}
            >
              {processing ? 'Generating Report...' : 'Generate Report'}
            </button>
          </div>
        </form>
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Analyzing documents and generating report...</p>
        </div>
      )}
      
      {reportPreview && !processing && (
        <div className="space-y-6 my-8">
          <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-4 py-3 border-b border-gray-200 dark:border-dark-border">
              <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
                Report Preview: {reportType === 'excel' ? 'Excel Workbook' : 'PowerPoint Presentation'}
              </h2>
            </div>
            
            <div className="p-4">
              <div className="mb-4 border border-gray-200 dark:border-dark-border rounded">
                {/* In a real app, this would be an actual preview image */}
                <div className="aspect-video bg-gray-100 dark:bg-dark-bg-primary flex items-center justify-center">
                  <div className="text-center p-6">
                    <div className="mb-2">
                      {reportType === 'excel' ? (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                        </svg>
                      )}
                    </div>
                    <p className="text-gray-500 dark:text-dark-text-secondary">
                      Preview image would be displayed here
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <h3 className="font-medium text-gray-900 dark:text-dark-text-primary mb-2">Report Sections</h3>
                <div className="space-y-3">
                  {reportPreview.sections.map((section, index) => (
                    <div key={index} className="border border-gray-200 dark:border-dark-border rounded p-3">
                      <h4 className="font-medium text-gray-800 dark:text-dark-text-primary">{section.title}</h4>
                      {section.content && (
                        <p className="text-sm text-gray-600 dark:text-dark-text-secondary mt-1">{section.content}</p>
                      )}
                      {section.charts && (
                        <div className="mt-1">
                          <span className="text-sm font-medium text-gray-700 dark:text-dark-text-secondary">Charts: </span>
                          <span className="text-sm text-gray-600 dark:text-dark-text-secondary">{section.charts.join(', ')}</span>
                        </div>
                      )}
                      {section.tables && (
                        <div className="mt-1">
                          <span className="text-sm font-medium text-gray-700 dark:text-dark-text-secondary">Tables: </span>
                          <span className="text-sm text-gray-600 dark:text-dark-text-secondary">
                            {section.tables.map(t => `${t.name} (${t.rows}x${t.columns})`).join(', ')}
                          </span>
                        </div>
                      )}
                      {section.bullets && (
                        <ul className="mt-1 text-sm text-gray-600 dark:text-dark-text-secondary list-disc list-inside">
                          {section.bullets.map((bullet, i) => (
                            <li key={i}>{bullet}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-dark-text-secondary">
                <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
                  Type: {reportType.charAt(0).toUpperCase() + reportType.slice(1)}
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
                  Style: {reportStyle.charAt(0).toUpperCase() + reportStyle.slice(1)}
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
                  Size: {reportPreview.estimatedPages}
                </div>
                <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
                  File size: {reportPreview.estimatedSize}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would trigger a regeneration
                alert('Regeneration functionality would be implemented here');
              }}
            >
              Regenerate with Changes
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                // In a real app, this would download the report
                alert('Download functionality would be implemented here');
              }}
            >
              Download Report
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Report Generation Agent
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload your source documents (data files, text documents, existing reports).</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Provide a detailed prompt describing the report you want to generate.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Select the report type (Excel or PowerPoint) and style preference.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the preview and make any necessary adjustments.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Download the final report for distribution or further editing.</li>
        </ol>
      </div>
    </div>
  );
};

export default ReportGeneration; 