import React from 'react';

const ResponseDisplay = ({ responseData, isLoading, error, submittedQuery }) => {
  
  if (isLoading) {
    return <div className="loading-spinner">Analyzing...</div>;
  }

  if (error) {
    return <div className="error-message"><strong>Error:</strong> {error}</div>;
  }

  if (!responseData) {
    return null;
  }

  console.log(responseData.data);
  const renderContent = () => {
    switch (responseData.type) {
      case 'table':
        const { headers, rows } = responseData.data;
        return (
          <table className="results-table">
            <thead>
              <tr>
                {headers.map((header, index) => <th key={index}>{header}</th>)}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        );
      case 'text':
        return <p className="text-response">{responseData.data}</p>;
      default:
        return <p className="error-message">Received an unknown response format.</p>;
    }
  };

  return (
    <div className="response-container">
      {submittedQuery && (
          <p>
              <span className="question-text">Question: </span>
              {submittedQuery}
          </p>
      )}
      <p className="answer-label">Answer:</p>
      {renderContent()}
    </div>
  );
};

export default ResponseDisplay;