import React, { useState, useEffect } from 'react';

// Assuming learningStylesOptions and timeOptions are defined elsewhere or passed as props
const learningStylesOptions = [
    "Visual", "Auditory", "Kinesthetic (Hands-on)", "Reading/Writing"
];
const timeOptions = ["Quick (5-15 mins)", "Medium (15-30 mins)", "Long (30-60 mins)", "Extended (60+ mins)"];


function FormComponent({ onSubmit, isLoading, initialData }) {
  const [goal, setGoal] = useState(initialData?.goal || '');
  const [familiarity, setFamiliarity] = useState(initialData?.familiarity || 'Beginner');
  const [styles, setStyles] = useState(initialData?.styles || []);
  const [timeAvailable, setTimeAvailable] = useState(initialData?.timeAvailable || '');
  const [specificFocus, setSpecificFocus] = useState(initialData?.specificFocus || '');
  // --- New State for Added Questions ---
  const [achieveGoal, setAchieveGoal] = useState(initialData?.achieveGoal || '');
  const [sessionScope, setSessionScope] = useState(initialData?.sessionScope || ''); // 'Deep Dive' or 'Quick Overview'


  // Pre-fill form if initialData exists (e.g., on restart)
  useEffect(() => {
      if (initialData) {
          setGoal(initialData.goal || '');
          setFamiliarity(initialData.familiarity || 'Beginner');
          setStyles(initialData.styles || []);
          setTimeAvailable(initialData.timeAvailable || '');
          setSpecificFocus(initialData.specificFocus || '');
          // --- Pre-fill new fields ---
          setAchieveGoal(initialData.achieveGoal || '');
          setSessionScope(initialData.sessionScope || '');
      }
  }, [initialData]);


  const handleStyleChange = (e) => {
    const { value, checked } = e.target;
    setStyles(prevStyles =>
      checked ? [...prevStyles, value] : prevStyles.filter(style => style !== value)
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!goal || !familiarity || styles.length === 0 || !timeAvailable || !sessionScope) {
        alert("Please fill in all required fields (Goal, Familiarity, Styles, Time, Session Scope).");
        return;
    }
    onSubmit({
      goal,
      familiarity,
      styles,
      timeAvailable: timeAvailable,
      specificFocus: specificFocus || null,
      achieveGoal,
      sessionScope
    });
  };

  const familiarityOptions = ['Beginner', 'Intermediate', 'Advanced'];

  return (
    <form onSubmit={handleSubmit} className="learning-form">
      <h3 style={{ marginBottom: '2rem'}}>Tell Us About Your Learning Goals</h3>

      <div className="form-group">
        <label htmlFor="goal">What topic do you want to learn or practice today? *</label>
        <input
          type="text"
          id="goal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g., Python basics, Origami Crane, CSS Flexbox"
          required
        />
      </div>

       {/* --- New Question 1 --- */}
       <div className="form-group">
        <label htmlFor="achieveGoal">What's one specific thing you hope to achieve with this topic?</label>
        <input
          type="text"
          id="achieveGoal"
          value={achieveGoal}
          onChange={(e) => setAchieveGoal(e.target.value)}
          placeholder="e.g., Understand loops, Fold my first model, Center a div"
        />
      </div>

      <div className="form-group">
        <label>How familiar are you with this topic? *</label>
        <div className="radio-group">
            {familiarityOptions.map(option => (
              <label key={option} className="modern-choice">
                <input
                  type="radio"
                  name="familiarity"
                  value={option}
                  checked={familiarity === option}
                  onChange={(e) => setFamiliarity(e.target.value)}
                  required
                />
                <span>{option}</span>
              </label>
            ))}
        </div>
      </div>

      <div className="form-group">
        <label>Preferred Learning Style(s) * (Choose at least one)</label>
        <div className="checkbox-group">
            {learningStylesOptions.map(style => (
              <label key={style} className="modern-choice">
                <input
                  type="checkbox"
                  value={style}
                  checked={styles.includes(style)}
                  onChange={handleStyleChange}
                />
                <span>{style}</span>
              </label>
            ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="timeAvailable">How much time do you have for this session? *</label>
        <select
          id="timeAvailable"
          value={timeAvailable}
          onChange={(e) => setTimeAvailable(e.target.value)}
          required
        >
          <option value="" disabled>Select time...</option>
          {timeOptions.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

       {/* --- New Question 2 --- */}
       <div className="form-group">
        <label>How deep do you want to go right now? *</label>
        <div className="radio-group">
            <label className="modern-choice">
                <input
                    type="radio"
                    name="sessionScope"
                    value="Quick Overview"
                    checked={sessionScope === 'Quick Overview'}
                    onChange={(e) => setSessionScope(e.target.value)}
                    required
                />
                <span>Quick Overview</span>
            </label>
            <label className="modern-choice">
                <input
                    type="radio"
                    name="sessionScope"
                    value="Deep Dive"
                    checked={sessionScope === 'Deep Dive'}
                    onChange={(e) => setSessionScope(e.target.value)}
                    required
                />
                <span>Deeper Dive</span>
            </label>
        </div>
       </div>

      <div className="form-group">
        <label htmlFor="specificFocus">Any other details or specific focus? (Optional)</label>
        <input
          type="text"
          id="specificFocus"
          value={specificFocus}
          onChange={(e) => setSpecificFocus(e.target.value)}
          placeholder="e.g., List comprehensions, Flexbox alignment"
        />
      </div>

      <button type="submit" disabled={isLoading} className="submit-button">
        {isLoading ? 'Analyzing...' : 'Find My Learning Path!'}
      </button>
    </form>
  );
}

export default FormComponent;