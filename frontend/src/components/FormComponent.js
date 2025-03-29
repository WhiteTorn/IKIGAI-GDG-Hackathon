import React, { useState, useEffect } from 'react';

function FormComponent({ onSubmit, isLoading, initialData }) {
  const [goal, setGoal] = useState('');
  const [familiarity, setFamiliarity] = useState(''); // e.g., 'Beginner', 'Intermediate', 'Advanced'
  const [styles, setStyles] = useState([]); // e.g., ['Visual', 'Auditory', 'Reading/Writing', 'Kinesthetic']
  const [timeAvailable, setTimeAvailable] = useState(''); // e.g., 'Short (15-30 mins)', 'Medium (30-60 mins)', 'Long (60+ mins)'
  const [specificFocus, setSpecificFocus] = useState('');

  // Pre-fill form if initialData is provided (e.g., on restart)
  useEffect(() => {
    if (initialData) {
      setGoal(initialData.goal || '');
      setFamiliarity(initialData.familiarity || '');
      setStyles(initialData.styles || []);
      setTimeAvailable(initialData.time_available || '');
      setSpecificFocus(initialData.specific_focus || '');
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
    if (!goal || !familiarity || styles.length === 0 || !timeAvailable) {
        alert("Please fill in all required fields (Goal, Familiarity, Styles, Time).");
        return;
    }
    onSubmit({
      goal,
      familiarity,
      styles,
      time_available: timeAvailable, // Match backend expected key
      specific_focus: specificFocus || null // Send null if empty
    });
  };

  const learningStylesOptions = ['Visual', 'Auditory', 'Reading/Writing', 'Kinesthetic (Hands-on)'];
  const timeOptions = ['Short (15-30 mins)', 'Medium (30-60 mins)', 'Long (60+ mins)'];
  const familiarityOptions = ['Beginner', 'Intermediate', 'Advanced'];

  return (
    <form onSubmit={handleSubmit} className="form-component">
      <h2>Your Learning Profile</h2>
      <p>Tell us about your learning preferences to personalize your session.</p>

      <div className="form-group">
        <label htmlFor="goal">What is your main learning goal for this session? *</label>
        <input
          type="text"
          id="goal"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          required
          placeholder="e.g., Understand Python lists, Learn basic CSS selectors"
        />
      </div>

      <div className="form-group radio-group">
        <label>How familiar are you with this topic? *</label>
        {familiarityOptions.map(option => (
          <label key={option}>
            <input
              type="radio"
              name="familiarity"
              value={option}
              checked={familiarity === option}
              onChange={(e) => setFamiliarity(e.target.value)}
              required
            /> {option}
          </label>
        ))}
      </div>

      <div className="form-group checkbox-group">
        <label>Preferred Learning Styles (select at least one): *</label>
        {learningStylesOptions.map(style => (
          <label key={style}>
            <input
              type="checkbox"
              value={style}
              checked={styles.includes(style)}
              onChange={handleStyleChange}
            /> {style}
          </label>
        ))}
      </div>

      <div className="form-group">
        <label htmlFor="timeAvailable">How much time do you have? *</label>
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

      <div className="form-group">
        <label htmlFor="specificFocus">Any specific area or concept you want to focus on? (Optional)</label>
        <input
          type="text"
          id="specificFocus"
          value={specificFocus}
          onChange={(e) => setSpecificFocus(e.target.value)}
          placeholder="e.g., List comprehensions, Flexbox alignment"
        />
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Analyzing...' : 'Find Learning Paths'}
      </button>
    </form>
  );
}

export default FormComponent;