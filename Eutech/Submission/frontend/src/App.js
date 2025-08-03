import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import QueryInput from './components/QueryInput';
import ResponseDisplay from './components/ResponseDisplay';

function App() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [responseData, setResponseData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);
    setResponseData(null);
    setSubmittedQuery(query);

    try {
      const apiUrl = process.env.REACT_APP_API_URL;
      const response = await axios.post(`${apiUrl}/analyze`, { query });
      setResponseData(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'An unexpected error occurred.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      setQuery('');
    }
  };

  return (
    <div className="app-container">
      <h1>IAQ Analysis Tool</h1>
      <QueryInput 
        query={query}
        setQuery={setQuery}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
      <ResponseDisplay 
        responseData={responseData}
        isLoading={isLoading}
        error={error}
        submittedQuery={submittedQuery}
      />
    </div>
  );
}

export default App;