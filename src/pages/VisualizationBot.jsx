import { useState } from 'react';
import FileUpload from '../components/FileUpload';

const VisualizationBot = () => {
  const [files, setFiles] = useState([]);
  const [visualizations, setVisualizations] = useState(null);
  const [processing, setProcessing] = useState(false);
  
  const handleUpload = (uploadedFiles) => {
    setFiles(uploadedFiles);
    
    // In a real application, you would send these files to a backend or API
    if (uploadedFiles.length > 0) {
      // Simulate API call
      setProcessing(true);
      setTimeout(() => {
        setProcessing(false);
        // Sample visualization data (this would come from backend in a real app)
        setVisualizations({
          charts: [
            {
              title: "Quarterly Sales Performance",
              description: "Simulated bar chart showing quarterly sales performance",
              type: "bar-chart"
            },
            {
              title: "Revenue by Department",
              description: "Simulated pie chart showing revenue distribution across departments",
              type: "pie-chart"
            },
            {
              title: "Year-Over-Year Growth",
              description: "Simulated line chart showing year-over-year growth trends",
              type: "line-chart"
            }
          ]
        });
      }, 2000);
    }
  };
  
  // Helper function to render chart placeholder based on type
  const renderChart = (chart) => {
    switch (chart.type) {
      case 'bar-chart':
        return (
          <div className="h-52 bg-gray-100 dark:bg-dark-bg-secondary rounded-md flex items-center justify-center p-4">
            <div className="flex items-end space-x-2 h-32">
              <div className="w-10 bg-tnb-red h-16 rounded-t"></div>
              <div className="w-10 bg-tnb-red h-24 rounded-t"></div>
              <div className="w-10 bg-tnb-red h-12 rounded-t"></div>
              <div className="w-10 bg-tnb-red h-28 rounded-t"></div>
              <div className="w-10 bg-tnb-blue h-20 rounded-t"></div>
              <div className="w-10 bg-tnb-blue h-32 rounded-t"></div>
              <div className="w-10 bg-tnb-blue h-16 rounded-t"></div>
              <div className="w-10 bg-tnb-blue h-22 rounded-t"></div>
            </div>
          </div>
        );
      case 'pie-chart':
        return (
          <div className="h-52 bg-gray-100 dark:bg-dark-bg-secondary rounded-md flex items-center justify-center p-4">
            <div className="h-32 w-32 rounded-full overflow-hidden">
              <div className="h-full w-full relative">
                <div className="absolute inset-0" style={{ 
                  background: 'conic-gradient(#E31837 0% 30%, #0055A4 30% 65%, #8BA3BD 65% 85%, #D9D9D9 85% 100%)' 
                }}></div>
              </div>
            </div>
          </div>
        );
      case 'line-chart':
        return (
          <div className="h-52 bg-gray-100 dark:bg-dark-bg-secondary rounded-md flex items-center justify-center p-4">
            <svg viewBox="0 0 200 100" className="w-full h-32" preserveAspectRatio="none">
              <polyline
                fill="none"
                stroke="#E31837"
                strokeWidth="3"
                points="
                  0,80
                  40,60
                  80,40
                  120,50
                  160,20
                  200,10
                "
              />
              <polyline
                fill="none"
                stroke="#0055A4"
                strokeWidth="3"
                points="
                  0,90
                  40,85
                  80,70
                  120,65
                  160,50
                  200,30
                "
              />
            </svg>
          </div>
        );
      default:
        return (
          <div className="h-52 bg-gray-100 dark:bg-dark-bg-secondary rounded-md flex items-center justify-center p-4">
            <p className="text-gray-500 dark:text-dark-text-secondary">Chart preview not available</p>
          </div>
        );
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          Visualization Bot
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Upload spreadsheets and data files to automatically generate insightful visualizations.
          Perfect for creating charts, graphs, and visual reports from raw data.
        </p>
      </div>
      
      <div className="mb-8">
        <FileUpload 
          onUpload={handleUpload} 
          allowedTypes={['.xls', '.xlsx', '.csv', '.json']} 
        />
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Processing your data...</p>
        </div>
      )}
      
      {visualizations && !processing && (
        <div className="space-y-8 my-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-dark-text-primary">
            Generated Visualizations
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {visualizations.charts.map((chart, index) => (
              <div key={index} className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
                <div className="p-4 border-b border-gray-200 dark:border-dark-border">
                  <h3 className="font-medium text-gray-900 dark:text-dark-text-primary">{chart.title}</h3>
                </div>
                {renderChart(chart)}
                <div className="p-4">
                  <p className="text-sm text-gray-600 dark:text-dark-text-secondary">{chart.description}</p>
                  <div className="mt-3 flex justify-end">
                    <button className="text-tnb-blue hover:text-blue-700 text-sm font-medium">
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex justify-end">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would download all charts
                alert('Download functionality would be implemented here');
              }}
            >
              Download All
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                setVisualizations(null);
                setFiles([]);
              }}
            >
              New Visualization
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the Visualization Bot
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Upload your data file (Excel, CSV, etc.) using the file uploader.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Wait while our AI analyzes your data patterns.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the automatically generated visualizations.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Download individual charts or the complete visualization set.</li>
        </ol>
      </div>
    </div>
  );
};

export default VisualizationBot; 