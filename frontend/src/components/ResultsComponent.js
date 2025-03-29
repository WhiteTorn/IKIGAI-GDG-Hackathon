import React from 'react';

function ResultsComponent({ summary, onRestart }) {
  return (
    <div className="results-component">
      <h2>Session Complete!</h2>
      <div className="results-summary">
        <p>{summary || "You've reached the end of this learning interaction."}</p>
      </div>
      <button onClick={onRestart}>Start New Session</button>
    </div>
  );
}

export default ResultsComponent;