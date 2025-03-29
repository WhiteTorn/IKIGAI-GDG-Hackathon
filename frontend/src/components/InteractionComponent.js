import React, { useState, useEffect } from 'react';

function InteractionComponent({ interactionData, onSubmitAnswer, isLoading }) {
  const [answer, setAnswer] = useState('');

  // Clear answer field when interaction data changes (new question)
  useEffect(() => {
      setAnswer('');
  }, [interactionData]);

  if (!interactionData) {
    return <p>Loading interaction...</p>; // Or handle error state
  }

  const { material, question_for_user, session_finished } = interactionData;

  // Should not happen in MVP as we go to results, but good practice
  if (session_finished) {
      return <p>Session has already finished.</p>
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitAnswer(answer);
    // Keep answer in textarea until next question loads or session ends
    // setAnswer(''); // Clear answer field after submission if preferred
  };

  return (
    <div className="interaction-component">
      <h2>Learning Interaction</h2>
      {material && (
        <div className="interaction-material">
          <h3>Material:</h3>
          <pre>{material}</pre> {/* Use pre for potential formatting */}
        </div>
      )}
      {question_for_user && (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="userAnswer" className="interaction-question">{question_for_user}</label>
            <textarea
              id="userAnswer"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Your answer here..."
              required
              disabled={isLoading}
            />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Submitting...' : 'Submit Answer'}
          </button>
        </form>
      )}
       {!question_for_user && !isLoading && <p>Waiting for next step...</p>}
    </div>
  );
}

export default InteractionComponent;