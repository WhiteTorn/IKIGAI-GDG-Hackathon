import React from 'react';

function PathSelectionComponent({ paths, onSelectPath, isLoading }) {
  if (isLoading && paths.length === 0) {
      return <p className="loading-indicator">Generating learning paths...</p>;
  }

  if (!paths || paths.length === 0) {
    return <p>No learning paths available. There might have been an issue.</p>;
  }

  return (
    <div className="path-selection-component">
      <h2>Choose Your Learning Path</h2>
      <p>Select one of the paths generated based on your profile:</p>
      <ul className="path-options">
        {paths.map((path, index) => (
          <li
            key={index}
            className="path-option"
            onClick={() => !isLoading && onSelectPath(path.name)} // Prevent click while loading next step
            role="button"
            tabIndex={0} // Make it focusable
            onKeyPress={(e) => (e.key === 'Enter' || e.key === ' ') && !isLoading && onSelectPath(path.name)} // Keyboard accessible
          >
            <h3>{path.name}</h3>
            <p>{path.overview}</p>
            <span>{path.duration}</span>
          </li>
        ))}
      </ul>
       {isLoading && <p className="loading-indicator">Starting session...</p>}
    </div>
  );
}

export default PathSelectionComponent;