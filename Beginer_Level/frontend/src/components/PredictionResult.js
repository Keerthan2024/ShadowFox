import React from 'react';
import './PredictionResult.css';

const PredictionResult = ({ result, loading }) => {
  if (loading) {
    return (
      <div className="prediction-result loading">
        <div className="loading-spinner"></div>
        <p>Analyzing property features...</p>
      </div>
    );
  }

  if (result?.error) {
    return (
      <div className="prediction-result error">
        <h3>❌ Prediction Error</h3>
        <p>{result.error}</p>
      </div>
    );
  }

  if (!result) return null;

  const getConfidenceColor = (confidence) => {
    if (confidence >= 85) return '#4CAF50';
    if (confidence >= 70) return '#FF9800';
    return '#F44336';
  };

  const getPriceCategory = (price) => {
    if (price >= 40) return { category: 'Luxury', emoji: '🏰', color: '#9C27B0' };
    if (price >= 25) return { category: 'High-End', emoji: '🏡', color: '#2196F3' };
    if (price >= 15) return { category: 'Mid-Range', emoji: '🏠', color: '#4CAF50' };
    return { category: 'Budget', emoji: '🏚️', color: '#FF5722' };
  };

  const priceInfo = getPriceCategory(result.prediction);

  return (
    <div className="prediction-result success">
      <h3>🎯 Price Prediction</h3>
      
      <div className="prediction-card">
        <div className="price-display">
          <span className="price-emoji">{priceInfo.emoji}</span>
          <span className="price-value" style={{color: priceInfo.color}}>
            {result.price_formatted}
          </span>
          <span className="price-category">{priceInfo.category}</span>
        </div>

        <div className="prediction-details">
          <div className="detail-item">
            <span className="detail-label">Confidence:</span>
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ 
                  width: `${result.confidence}%`,
                  backgroundColor: getConfidenceColor(result.confidence)
                }}
              ></div>
              <span className="confidence-text">{result.confidence}%</span>
            </div>
          </div>

          <div className="detail-item">
            <span className="detail-label">Model:</span>
            <span className="detail-value">{result.model}</span>
          </div>

          <div className="detail-item">
            <span className="detail-label">Accuracy:</span>
            <span className="detail-value">{result.accuracy}</span>
          </div>
        </div>
      </div>

      <div className="prediction-insights">
        <h4>💡 Key Insights</h4>
        <ul>
          <li>Based on 1970s Boston housing data (adjusted for inflation)</li>
          <li>Model trained on 506 real estate transactions</li>
          <li>Considers 13 key factors including location, size, and amenities</li>
          <li>91.79% accuracy with $1.90K average error</li>
        </ul>
      </div>
    </div>
  );
};

export default PredictionResult;
