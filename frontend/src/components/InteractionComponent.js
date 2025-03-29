import React, { useState, useEffect } from 'react';

function InteractionComponent({ interactionData, onSubmitAnswer, isLoading }) {
  const [answer, setAnswer] = useState('');

  // Clear answer field when interaction data changes (new question)
  useEffect(() => {
      setAnswer('');
  }, [interactionData]);

  if (!interactionData) {
    // Simple, clean loading state
    return <p className="loading-indicator">Loading interaction...</p>;
  }

  const { material, question_for_user, session_finished } = interactionData;

  // Clean handling of finished state
  if (session_finished) {
      // Consider a more styled component later if needed, but <p> is simple
      return <p>Session has finished.</p>;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    // Corrected logic: Submit if there's an answer OR if there's no question (Continue button case)
    if (answer.trim() || !question_for_user) {
        onSubmitAnswer(answer); // Sends empty answer for "Continue"
        // setAnswer(''); // State is already cleared by useEffect on data change
    }
  };

  // The existing structure utilizes the CSS classes effectively for a modern look.
  return (
    <div className="interaction-container">
      {/* Loading overlay provides clear feedback during processing */}
      {isLoading && <div className="loading-overlay">Processing...</div>}

      {/* Material Section: Uses h3 (with border) and p styles */}
      {material && (
        <div className="material-section">
          <h3>Learning Material:</h3>
          {/* pre-wrap preserves formatting from the backend */}
          <p style={{ whiteSpace: 'pre-wrap' }}>{material}</p>
        </div>
      )}

      {/* Question Section: Uses h3, p, textarea, and specific button styles */}
      {question_for_user && (
        <div className="question-section">
          <h3>Question:</h3>
          <p>{question_for_user}</p>
          <form onSubmit={handleSubmit}>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Your answer..."
              rows="4" // Keep reasonable default size
              disabled={isLoading}
              // Inherits modern styling from App.css
            />
            <button
              type="submit"
              disabled={isLoading || !answer.trim()} // Also disable if answer is empty
              className="submit-answer-button" // Uses the specific "ghost" button style
            >
              Submit Answer
            </button>
          </form>
        </div>
      )}

      {/* Continue Button Section: Appears when material is shown, but no question yet */}
      {material && !question_for_user && !isLoading && (
           // Using a form allows reusing the handleSubmit logic
           <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}> {/* Add some space */}
                {/* This button inherits the base 'button' style from App.css */}
                <button type="submit" disabled={isLoading}>
                    Continue
                </button>
           </form>
       )}

       {/* Fallback message if waiting without material/question */}
       {!material && !question_for_user && !isLoading && (
           <p>Waiting for next step...</p>
       )}
    </div>
  );
}

export default InteractionComponent;