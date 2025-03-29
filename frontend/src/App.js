import React, { useState, useCallback, useEffect } from 'react';
import FormComponent from './components/FormComponent';
import PathSelectionComponent from './components/PathSelectionComponent';
import InteractionComponent from './components/InteractionComponent';
import ResultsComponent from './components/ResultsComponent';
import './App.css';

// Use environment variable for API URL or default to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

function App() {
  const [currentStep, setCurrentStep] = useState('form'); // 'form', 'paths', 'interaction', 'results'
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [learningPaths, setLearningPaths] = useState([]);
  const [interactionData, setInteractionData] = useState(null); // { material, question_for_user, session_finished, summary }
  const [finalSummary, setFinalSummary] = useState('');
  const [formDataForRetry, setFormDataForRetry] = useState(null); // Store form data if needed for retry/restart

  // --- API Call Functions ---

  const handleApiCall = useCallback(async (endpoint, method = 'GET', body = null) => {
    setIsLoading(true);
    setError('');
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };
      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

      if (!response.ok) {
        let errorMsg = `HTTP error! status: ${response.status}`;
        try {
            const errData = await response.json();
            errorMsg = errData.message || errorMsg;
        } catch (e) {
            // Ignore if response is not JSON
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      if (data.status !== 'success') {
        throw new Error(data.message || 'API request failed');
      }
      return data; // Return the payload part of the response

    } catch (err) {
      console.error("API Call Error:", err);
      setError(err.message || 'An unexpected error occurred.');
      return null; // Indicate failure
    } finally {
      setIsLoading(false);
    }
  }, []); // No dependencies needed for useCallback here

  const handleFormSubmit = useCallback(async (formData) => {
    setFormDataForRetry(formData); // Save form data
    const data = await handleApiCall('/analyze_form', 'POST', formData);
    if (data) {
      // Directly fetch paths after successful form submission
      const pathData = await handleApiCall('/get_learning_paths', 'GET');
      if (pathData && pathData.paths) {
        setLearningPaths(pathData.paths);
        setCurrentStep('paths');
      } else {
         setError(error || 'Failed to fetch learning paths after submitting form.');
      }
    }
  }, [handleApiCall, error]); // Add error to dependency array if needed

  const handlePathSelection = useCallback(async (pathName) => {
    const data = await handleApiCall('/start_quiz', 'POST', { chosen_path_name: pathName });
    if (data && data.interaction) {
      setInteractionData(data.interaction);
      setCurrentStep('interaction');
    }
  }, [handleApiCall]);

  const handleInteractionSubmit = useCallback(async (answer) => {
    const data = await handleApiCall('/submit_answer', 'POST', { answer });
    if (data && data.interaction) {
      setInteractionData(data.interaction); // Update interaction state (might contain summary)
      if (data.interaction.session_finished) {
        setFinalSummary(data.interaction.summary || 'Session finished.');
        setCurrentStep('results');
      }
      // If session_finished is false, we'd stay in 'interaction' step
      // but for MVP, it always finishes here.
    }
  }, [handleApiCall]);

  const handleRestart = () => {
      // Reset state to initial values
      setCurrentStep('form');
      setIsLoading(false);
      setError('');
      setLearningPaths([]);
      setInteractionData(null);
      setFinalSummary('');
      // Optionally clear formDataForRetry or keep it to pre-fill form
      // setFormDataForRetry(null);
  };


  // --- Rendering Logic ---

  const renderStep = () => {
    switch (currentStep) {
      case 'form':
        return <FormComponent onSubmit={handleFormSubmit} isLoading={isLoading} initialData={formDataForRetry} />;
      case 'paths':
        return <PathSelectionComponent paths={learningPaths} onSelectPath={handlePathSelection} isLoading={isLoading} />;
      case 'interaction':
        return <InteractionComponent interactionData={interactionData} onSubmitAnswer={handleInteractionSubmit} isLoading={isLoading} />;
      case 'results':
        return <ResultsComponent summary={finalSummary} onRestart={handleRestart} />;
      default:
        return <p>Invalid step.</p>;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Learning Assistant MVP</h1>
      </header>
      <main className="App-main">
        {error && <p className="error-message">Error: {error}</p>}
        {isLoading && <p className="loading-indicator">Loading...</p>}
        {renderStep()}
      </main>
      <footer className="App-footer">
        <p>GDG EdTech Hackathon Project</p>
      </footer>
    </div>
  );
}

export default App;