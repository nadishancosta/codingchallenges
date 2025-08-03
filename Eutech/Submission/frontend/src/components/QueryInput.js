import React from 'react';

const QueryInput = ({ query, setQuery, handleSubmit, isLoading }) => {
  return (
    <form onSubmit={handleSubmit} className="query-form">
      <label htmlFor="query-input" className="query-label">Enter your query</label>
      <input
        id="query-input"
        type="text"
        className="query-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g., What was the average co2 level per day?"
        disabled={isLoading}
      />
      <button id = "submit_btn" type="submit" disabled={isLoading}>Submit</button>
    </form>
  );
};

export default QueryInput;