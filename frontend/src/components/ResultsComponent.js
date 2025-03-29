import React from 'react';

// Helper function to render summary sections safely
const renderSummarySection = (title, content) => {
    if (!content || typeof content !== 'string' || content.trim() === '' || content.toLowerCase() === 'n/a') {
        return null; // Don't render empty/invalid sections
    }
    return (
        <div className="summary-section">
            <h4>{title}</h4>
            <p>{content}</p>
        </div>
    );
};


function ResultsComponent({ summary, topicName, onRestart, onContinue, isLoading }) {

  // Default structure in case summary is null or not an object
  const defaultSummary = {
      recap: "You've reached the end of this learning block.",
      strengths: "",
      areas_for_improvement: "",
      next_step_suggestion: "",
      motivation: "Great effort!"
  };

  // Use summary if it's a valid object, otherwise use default or simple string
  let displaySummary;
  if (summary && typeof summary === 'object' && summary !== null) {
      displaySummary = { ...defaultSummary, ...summary }; // Merge with default to ensure all keys exist
  } else if (typeof summary === 'string' && summary.trim() !== '') {
       displaySummary = { ...defaultSummary, recap: summary }; // Use string as recap
  }
  else {
      displaySummary = defaultSummary;
  }


  return (
    <div className="results-component">
      <h2>Session Debrief: {topicName || 'Learning Topic'}</h2>

      <div className="results-summary-structured">
        {renderSummarySection("Session Recap", displaySummary.recap)}
        {renderSummarySection("You Did Well On", displaySummary.strengths)}
        {renderSummarySection("Keep Practicing", displaySummary.areas_for_improvement)}
        {renderSummarySection("Next Steps Suggestion", displaySummary.next_step_suggestion)}
        {renderSummarySection("Keep Going!", displaySummary.motivation)}
      </div>

      <div className="results-actions">
         <h3>What's Next?</h3>
         <div className="action-buttons">
            <button onClick={onContinue} disabled={isLoading} className="continue-button">
              {isLoading ? 'Loading...' : `Continue Learning: ${topicName || 'This Topic'}`}
            </button>
            <button onClick={onRestart} disabled={isLoading} className="restart-button">
              {isLoading ? 'Loading...' : 'Explore a New Topic'}
            </button>
         </div>
      </div>
    </div>
  );
}

export default ResultsComponent;