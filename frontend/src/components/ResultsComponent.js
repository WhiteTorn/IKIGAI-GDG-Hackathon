import React from 'react';

// Helper function to render summary sections safely with emojis
const renderSummarySection = (title, content, emoji) => {
    if (!content || typeof content !== 'string' || content.trim() === '' || content.toLowerCase() === 'n/a') {
        return null; // Don't render empty/invalid sections
    }
    return (
        <div className="summary-section">
            <h4>{emoji} {title}</h4>
            <p>{content}</p>
        </div>
    );
};


function ResultsComponent({ summary, topicName, onRestart, onContinue, isLoading }) {

  // Default structure in case summary is null or not an object
  const defaultSummary = {
      recap: "You've completed this learning block! Let's see how you did.", // More engaging default
      strengths: "Every step forward is progress!",
      areas_for_improvement: "Identifying areas to grow is key to mastery.",
      next_step_suggestion: "Ready for the next challenge?",
      motivation: "Keep up the fantastic effort! 🔥" // Added default emoji
  };

  // Use summary if it's a valid object, otherwise use default or simple string
  let displaySummary;
  if (summary && typeof summary === 'object' && summary !== null) {
      // Ensure all keys exist by merging with default, prioritizing received summary
      displaySummary = { ...defaultSummary, ...summary };
      // Add default emojis if not provided by AI (though AI prompt doesn't ask for them)
      displaySummary.motivation = displaySummary.motivation || defaultSummary.motivation;
  } else if (typeof summary === 'string' && summary.trim() !== '') {
       displaySummary = { ...defaultSummary, recap: summary }; // Use string as recap
  }
  else {
      displaySummary = defaultSummary;
  }


  return (
    <div className="results-component game-profile"> {/* Added 'game-profile' class */}
      <h2>🏆 Session Complete! 🏆</h2>
      <h3>Topic: {topicName || 'Learning Adventure'}</h3>

      <div className="results-summary-structured">
        {/* Pass emojis and potentially adjusted titles */}
        {renderSummarySection("Mission Recap", displaySummary.recap, "📝")}
        {renderSummarySection("Your Strengths", displaySummary.strengths, "💪")}
        {renderSummarySection("Level Up Areas", displaySummary.areas_for_improvement, "🌱")}
        {renderSummarySection("Next Quest", displaySummary.next_step_suggestion, "🚀")}
        {renderSummarySection("Keep Going!", displaySummary.motivation, "🌟")}
      </div>

      <div className="results-actions">
         <h3>Choose Your Next Move:</h3>
         <div className="action-buttons">
            {/* Added emojis to buttons */}
            <button onClick={onContinue} disabled={isLoading} className="continue-button">
              {isLoading ? 'Loading...' : `▶️ Continue: ${topicName || 'This Topic'}`}
            </button>
            <button onClick={onRestart} disabled={isLoading} className="restart-button">
              {isLoading ? 'Loading...' : '🗺️ Explore New Topic'}
            </button>
         </div>
      </div>
    </div>
  );
}

export default ResultsComponent;