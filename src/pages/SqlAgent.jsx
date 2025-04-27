import { useState } from 'react';

const SqlAgent = () => {
  const [query, setQuery] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [results, setResults] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [databases, setDatabases] = useState([
    { id: 1, name: 'Customer Database', tables: ['customers', 'orders', 'products'] },
    { id: 2, name: 'Employee Database', tables: ['employees', 'departments', 'salaries'] },
    { id: 3, name: 'Financial Database', tables: ['transactions', 'accounts', 'budgets'] }
  ]);
  const [selectedDb, setSelectedDb] = useState(1);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    // In a real application, this would be an API call to the backend
    setProcessing(true);
    
    // Simulate API call
    setTimeout(() => {
      // For demo purposes, generate a sample SQL query based on the natural language query
      let generatedQuery = '';
      const dbName = databases.find(db => db.id === selectedDb).name;
      
      if (query.toLowerCase().includes('customer') && query.toLowerCase().includes('order')) {
        generatedQuery = `SELECT c.customer_name, o.order_date, o.total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date > '2023-01-01'
ORDER BY o.total_amount DESC
LIMIT 10;`;
      } else if (query.toLowerCase().includes('employee') && query.toLowerCase().includes('salary')) {
        generatedQuery = `SELECT e.first_name, e.last_name, d.department_name, s.salary
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN salaries s ON e.employee_id = s.employee_id
WHERE s.salary > 50000
ORDER BY s.salary DESC;`;
      } else if (query.toLowerCase().includes('transaction')) {
        generatedQuery = `SELECT t.transaction_date, t.amount, a.account_name
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
WHERE t.transaction_date BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY t.amount DESC;`;
      } else {
        generatedQuery = `-- Example SQL query based on your question
SELECT * 
FROM ${databases.find(db => db.id === selectedDb).tables[0]}
WHERE status = 'active'
LIMIT 10;`;
      }
      
      setSqlQuery(generatedQuery);
      
      // Sample query results
      const sampleResults = {
        columns: ['Name', 'Value', 'Category', 'Date'],
        rows: [
          ['Alpha Corp', '$12,500', 'Enterprise', '2023-10-15'],
          ['Beta LLC', '$8,750', 'SMB', '2023-10-12'],
          ['Gamma Inc', '$7,200', 'Enterprise', '2023-10-10'],
          ['Delta Services', '$6,500', 'SMB', '2023-10-08'],
          ['Epsilon Technologies', '$5,800', 'Startup', '2023-10-05']
        ],
        summary: {
          totalRows: 5,
          executionTime: '0.023 seconds',
          dbUsed: dbName
        }
      };
      
      setResults(sampleResults);
      setProcessing(false);
    }, 1500);
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary mb-2">
          SQL Agent
        </h1>
        <p className="text-gray-600 dark:text-dark-text-secondary">
          Ask questions about your data in plain English, and the SQL Agent will convert them to SQL queries
          and return the answers. No SQL knowledge required.
        </p>
      </div>
      
      <div className="bg-white dark:bg-dark-bg-secondary rounded-lg shadow-sm p-6 mb-8 border border-gray-200 dark:border-dark-border">
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="database" className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Select Database
            </label>
            <select
              id="database"
              className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
              value={selectedDb}
              onChange={(e) => setSelectedDb(parseInt(e.target.value))}
            >
              {databases.map(db => (
                <option key={db.id} value={db.id}>{db.name}</option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 dark:text-dark-text-secondary mb-1">
              Your Question
            </label>
            <textarea
              id="query"
              rows="3"
              className="w-full rounded-md border border-gray-300 dark:border-dark-border py-2 px-3 bg-white dark:bg-dark-bg-primary text-gray-900 dark:text-dark-text-primary focus:outline-none focus:ring-2 focus:ring-tnb-blue"
              placeholder="Example: Show me the top 10 customers by order value from last month"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            ></textarea>
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              className="btn-primary"
              disabled={processing || !query.trim()}
            >
              {processing ? 'Processing...' : 'Generate SQL & Results'}
            </button>
          </div>
        </form>
      </div>
      
      {processing && (
        <div className="my-8 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-tnb-blue"></div>
          <p className="mt-2 text-gray-600 dark:text-dark-text-secondary">Generating SQL and fetching results...</p>
        </div>
      )}
      
      {sqlQuery && !processing && (
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-2">
            Generated SQL Query
          </h2>
          <div className="bg-gray-50 dark:bg-dark-bg-primary border border-gray-200 dark:border-dark-border rounded-md p-4 overflow-x-auto">
            <pre className="text-sm text-gray-800 dark:text-dark-text-primary whitespace-pre-wrap">
              {sqlQuery}
            </pre>
          </div>
        </div>
      )}
      
      {results && !processing && (
        <div className="space-y-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-2">
            Query Results
          </h2>
          
          <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-border rounded-lg shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-border">
                <thead className="bg-gray-50 dark:bg-dark-bg-primary">
                  <tr>
                    {results.columns.map((column, index) => (
                      <th 
                        key={index}
                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-dark-text-secondary uppercase tracking-wider"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-dark-bg-secondary divide-y divide-gray-200 dark:divide-dark-border">
                  {results.rows.map((row, rowIndex) => (
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
          
          <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-dark-text-secondary">
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
              Total rows: {results.summary.totalRows}
            </div>
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
              Execution time: {results.summary.executionTime}
            </div>
            <div className="bg-gray-50 dark:bg-dark-bg-primary px-3 py-1 rounded-full">
              Database: {results.summary.dbUsed}
            </div>
          </div>
          
          <div className="flex justify-end mt-4">
            <button
              type="button"
              className="btn-secondary mr-3"
              onClick={() => {
                // In a real app, this would export data to CSV or Excel
                alert('Export functionality would be implemented here');
              }}
            >
              Export Results
            </button>
            <button
              type="button"
              className="btn-primary"
              onClick={() => {
                setQuery('');
                setSqlQuery('');
                setResults(null);
              }}
            >
              New Query
            </button>
          </div>
        </div>
      )}
      
      <div className="bg-gray-50 dark:bg-dark-bg-secondary rounded-lg p-6 mt-8">
        <h3 className="text-lg font-medium text-gray-900 dark:text-dark-text-primary mb-4">
          How to use the SQL Agent
        </h3>
        <ol className="list-decimal pl-5 space-y-2">
          <li className="text-gray-600 dark:text-dark-text-secondary">Select the database you want to query.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Ask your question in plain English, being as specific as possible.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Review the generated SQL query for accuracy (optional).</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Examine the query results for your answer.</li>
          <li className="text-gray-600 dark:text-dark-text-secondary">Export the results if needed for further analysis.</li>
        </ol>
      </div>
    </div>
  );
};

export default SqlAgent; 