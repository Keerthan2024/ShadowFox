import React, { useState } from 'react';
import './PredictionForm.css';

const PredictionForm = ({ onPredict, features, loading }) => {
  const [formData, setFormData] = useState({
    CRIM: 0.26,
    ZN: 0,
    INDUS: 9.69,
    CHAS: 0,
    NOX: 0.538,
    RM: 6.2,
    AGE: 77.5,
    DIS: 3.2,
    RAD: 5,
    TAX: 330,
    PTRATIO: 19.05,
    B: 391.44,
    LSTAT: 11.36
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  const loadPreset = (preset) => {
    const presets = {
      luxury: {
        CRIM: 0.01, ZN: 25, INDUS: 2.3, CHAS: 1, NOX: 0.4, RM: 8.0,
        AGE: 30, DIS: 6.0, RAD: 1, TAX: 200, PTRATIO: 15.0, B: 396, LSTAT: 3.0
      },
      average: {
        CRIM: 0.26, ZN: 0, INDUS: 9.69, CHAS: 0, NOX: 0.538, RM: 6.2,
        AGE: 77.5, DIS: 3.2, RAD: 5, TAX: 330, PTRATIO: 19.05, B: 391.44, LSTAT: 11.36
      },
      budget: {
        CRIM: 15.0, ZN: 0, INDUS: 18.1, CHAS: 0, NOX: 0.7, RM: 4.5,
        AGE: 95, DIS: 1.5, RAD: 24, TAX: 666, PTRATIO: 20.2, B: 350, LSTAT: 25.0
      }
    };
    setFormData(presets[preset]);
  };

  return (
    <div className="prediction-form">
      <h2>🔮 Predict House Price</h2>
      
      <div className="presets">
        <button onClick={() => loadPreset('luxury')} className="preset-btn luxury">
          🏰 Luxury Home
        </button>
        <button onClick={() => loadPreset('average')} className="preset-btn average">
          🏠 Average Home
        </button>
        <button onClick={() => loadPreset('budget')} className="preset-btn budget">
          🏚️ Budget Home
        </button>
      </div>

      <form onSubmit={handleSubmit} className="form">
        {Object.entries(features).map(([key, info]) => (
          <div key={key} className="form-group">
            <label htmlFor={key}>
              {info.name}
              <span className="feature-description">{info.description}</span>
            </label>
            <input
              type={key === 'CHAS' ? 'select' : 'number'}
              id={key}
              name={key}
              value={formData[key]}
              onChange={handleChange}
              min={info.min}
              max={info.max}
              step={key === 'CHAS' || key === 'RAD' || key === 'TAX' ? 1 : 0.01}
              required
            />
            <span className="unit">{info.unit}</span>
          </div>
        ))}

        <button 
          type="submit" 
          className={`predict-btn ${loading ? 'loading' : ''}`}
          disabled={loading}
        >
          {loading ? '🔄 Predicting...' : '🎯 Predict Price'}
        </button>
      </form>
    </div>
  );
};

export default PredictionForm;
