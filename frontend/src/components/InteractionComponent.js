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
    if (answer.trim() || question_for_user) { // Allow submitting even if question is null (e.g., initial step)
        onSubmitAnswer(answer);
        setAnswer(''); // Clear input after submit
    }
  };

  return (
    <div className="interaction-container">
      {isLoading && <div className="loading-overlay">Processing...</div>}
      {material && (
        <div className="material-section">
          <h3>Learning Material:</h3>
          <p style={{ whiteSpace: 'pre-wrap' }}>{material}</p>
        </div>
      )}
      {question_for_user && (
        <div className="question-section">
          <h3>Question:</h3>
          <p>{question_for_user}</p>
          <form onSubmit={handleSubmit}>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Your answer..."
              rows="4"
              disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>Submit Answer</button>
          </form>
        </div>
      )}
       {!question_for_user && !isLoading && <p>Waiting for next step...</p>}
       {material && !question_for_user && (
           <form onSubmit={handleSubmit}>
                <button type="submit" disabled={isLoading}>Continue</button>
           </form>
       )}
    </div>
  );
}

export default InteractionComponent;