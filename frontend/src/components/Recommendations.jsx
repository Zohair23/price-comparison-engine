// Recommendations.jsx - shows similar products user might like
// not being used right now but kept for future

import React from 'react';
import './Recommendations.css';

export default function Recommendations({ recommendations }) {
  // if no recommendations, show message
  if (!recommendations || recommendations.length === 0) {
    return <div className="no-data">No recommendations available</div>;
  }

  return (
    <div className="recommendations">
      <h3>Recommended Products</h3>
      <div className="rec-list">
        {/* loop through each recommendation */}
        {recommendations.map((rec) => (
          <div key={rec.id} className="rec-item">
            <img src={rec.product?.image_url || 'https://via.placeholder.com/100'} alt={rec.product?.name} />
            <div className="rec-info">
              <h4>{rec.product?.name}</h4>
              <p className="rec-type">{rec.type}</p>
              <div className="score-bar">
                <div className="score" style={{ width: `${rec.score * 100}%` }}></div>
              </div>
              <p className="score-text">{(rec.score * 100).toFixed(0)}% match</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
