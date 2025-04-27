import { useState, useRef } from 'react';

const FileUpload = ({ onUpload, allowedTypes = ['.pdf', '.doc', '.docx', '.xls', '.xlsx'] }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const uploadedFiles = Array.from(e.dataTransfer.files);
      setFiles(uploadedFiles);
      if (onUpload) onUpload(uploadedFiles);
    }
  };
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const uploadedFiles = Array.from(e.target.files);
      setFiles(uploadedFiles);
      if (onUpload) onUpload(uploadedFiles);
    }
  };
  
  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div
      className={`
        border-2 border-dashed rounded-lg p-8 
        transition-colors text-center
        ${isDragging 
          ? 'border-tnb-blue bg-blue-50 dark:bg-blue-900/20' 
          : files.length 
            ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
            : 'border-gray-300 dark:border-dark-border hover:border-tnb-blue dark:hover:border-tnb-blue dark:bg-dark-bg-secondary'
        }
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept={allowedTypes.join(',')}
        className="hidden"
      />
      
      <div className="space-y-4">
        {files.length > 0 ? (
          <>
            <div className="flex justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
              {files.length} file{files.length > 1 ? 's' : ''} uploaded!
            </h3>
            <ul className="text-sm text-gray-600 dark:text-dark-text-secondary max-w-xs mx-auto">
              {files.map((file, index) => (
                <li key={index} className="truncate">{file.name}</li>
              ))}
            </ul>
            <button
              type="button"
              onClick={handleButtonClick}
              className="btn-secondary"
            >
              Upload Different Files
            </button>
          </>
        ) : (
          <>
            <div className="flex justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400 dark:text-dark-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary">
              Drag and drop your files here
            </h3>
            <p className="text-sm text-gray-600 dark:text-dark-text-secondary max-w-xs mx-auto mb-4">
              Supported file types: {allowedTypes.join(', ')}
            </p>
            
            <div className="mt-6 flex items-center justify-center">
              <div className="flex items-center">
                <div className="h-px w-12 bg-gray-300 dark:bg-dark-border"></div>
                <span className="mx-4 text-sm text-gray-500 dark:text-dark-text-secondary">or</span>
                <div className="h-px w-12 bg-gray-300 dark:bg-dark-border"></div>
              </div>
            </div>
            
            <div className="mt-4">
              <button
                type="button"
                onClick={handleButtonClick}
                className="btn-primary px-6 py-2"
              >
                Browse Files
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default FileUpload; 