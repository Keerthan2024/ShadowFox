import React, { useState } from 'react';
import './PredictionForm.css';

const PredictionForm = ({ onPredict, features, loading }) => {
  const [formData, setFormData] = useState({
    car_name: 'city',
    year: 2018,
    present_price: 5.59,
    kms_driven: 27000,
    fuel_type: 'Petrol',
    seller_type: 'Dealer',
    transmission: 'Manual',
    owner: 0
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict(formData);
  };

  const loadPreset = (preset) => {
    const presets = {
      luxury: {
        car_name: 'fortuner',
        year: 2020,
        present_price: 35.0,
        kms_driven: 15000,
        fuel_type: 'Diesel',
        seller_type: 'Dealer',
        transmission: 'Automatic',
        owner: 0
      },
      average: {
        car_name: 'swift',
        year: 2017,
        present_price: 6.87,
        kms_driven: 35000,
        fuel_type: 'Petrol',
        seller_type: 'Dealer',
        transmission: 'Manual',
        owner: 0
      },
      budget: {
        car_name: 'alto 800',
        year: 2014,
        present_price: 3.5,
        kms_driven: 60000,
        fuel_type: 'Petrol',
        seller_type: 'Individual',
        transmission: 'Manual',
        owner: 1
      }
    };
    setFormData(presets[preset]);
  };

  return (
    <div className="prediction-form">
      <h2>🔮 Predict Car Price</h2>
      
      <div className="presets">
        <button 
          type="button"
          onClick={() => loadPreset('luxury')} 
          className="preset-btn luxury"
        >
          🏰 Luxury Car
        </button>
        <button 
          type="button"
          onClick={() => loadPreset('average')} 
          className="preset-btn average"
        >
          🚗 Average Car
        </button>
        <button 
          type="button"
          onClick={() => loadPreset('budget')} 
          className="preset-btn budget"
        >
          🚙 Budget Car
        </button>
      </div>

      <form onSubmit={handleSubmit} className="form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="car_name">Car Model</label>
            <select
              id="car_name"
              name="car_name"
              value={formData.car_name}
              onChange={handleChange}
              required
            >
              <option value="city">City</option>
              <option value="swift">Swift</option>
              <option value="dzire">Dzire</option>
              <option value="i20">i20</option>
              <option value="verna">Verna</option>
              <option value="corolla altis">Corolla Altis</option>
              <option value="fortuner">Fortuner</option>
              <option value="innova">Innova</option>
              <option value="baleno">Baleno</option>
              <option value="brio">Brio</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="year">Year</label>
            <input
              type="number"
              id="year"
              name="year"
              value={formData.year}
              onChange={handleChange}
              min="2003"
              max="2024"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="present_price">Present Price (₹ Lakh)</label>
            <input
              type="number"
              id="present_price"
              name="present_price"
              value={formData.present_price}
              onChange={handleChange}
              min="0.32"
              max="92.6"
              step="0.1"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="kms_driven">KM Driven</label>
            <input
              type="number"
              id="kms_driven"
              name="kms_driven"
              value={formData.kms_driven}
              onChange={handleChange}
              min="500"
              max="500000"
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="fuel_type">Fuel Type</label>
            <select
              id="fuel_type"
              name="fuel_type"
              value={formData.fuel_type}
              onChange={handleChange}
              required
            >
              <option value="Petrol">Petrol</option>
              <option value="Diesel">Diesel</option>
              <option value="CNG">CNG</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="seller_type">Seller Type</label>
            <select
              id="seller_type"
              name="seller_type"
              value={formData.seller_type}
              onChange={handleChange}
              required
            >
              <option value="Dealer">Dealer</option>
              <option value="Individual">Individual</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="transmission">Transmission</label>
            <select
              id="transmission"
              name="transmission"
              value={formData.transmission}
              onChange={handleChange}
              required
            >
              <option value="Manual">Manual</option>
              <option value="Automatic">Automatic</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="owner">Number of Owners</label>
            <input
              type="number"
              id="owner"
              name="owner"
              value={formData.owner}
              onChange={handleChange}
              min="0"
              max="3"
              required
            />
          </div>
        </div>

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
