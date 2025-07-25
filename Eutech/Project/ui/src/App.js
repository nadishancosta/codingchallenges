import React, { useState } from 'react';
import './App.css';

// A component to render the table dynamically
const ResultTable = ({ data }) => {
  if (!data || data.length === 0) {
    return null;
  }

  const headers = Object.keys(data[0]);

  return (
    <table>
      <thead>
        <tr>
          {headers.map(header => <th key={header}>{header}</th>)}
        </tr>
      </thead>
      <tbody>
        {data.map((row, index) => (
          <tr key={index}>
            {headers.map(header => <td key={header}>{row[header]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
};


function App() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data.answer);

    } catch (error) {
      console.error("Fetch error:", error);
      setResult({ text: `Error: Could not connect to the backend. ${error.message}`, table: null });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>AI Agent: Air Quality Analysis</h1>
      </header>
      <main>
        <div className="query-box">
          <form onSubmit={handleSubmit}>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What is the average temperature in Room A?"
              rows="3"
            />
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Ask'}
            </button>
          </form>
        </div>
        
        {isLoading && <div className="loader"></div>}
        
        {result && (
          <div className="result-box">
            <p>{result.text}</p>
            {result.table && <ResultTable data={result.table} />}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;