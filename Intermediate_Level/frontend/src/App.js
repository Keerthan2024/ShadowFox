import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PredictionForm from './components/PredictionForm';
import PredictionResult from './components/PredictionResult';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [features, setFeatures] = useState({});
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkApiHealth();
    loadFeatures();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/health');
      setApiStatus(response.data.model_loaded ? 'connected' : 'error');
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const loadFeatures = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/features');
      setFeatures(response.data.features);
    } catch (error) {
      console.error('Failed to load features:', error);
    }
  };

  const handlePredict = async (formData) => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/predict', formData);
      const result = response.data;
      setPrediction(result);
      
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        prediction: result.prediction,
        input: formData
      };
      setPredictionHistory(prev => [historyItem, ...prev.slice(0, 9)]);
      
    } catch (error) {
      console.error('Prediction failed:', error);
      setPrediction({
        error: error.response?.data?.error || 'Prediction failed'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App car-theme">
      {/* Background Effects */}
      <div className="background-particles">
        {[...Array(25)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 10}s`
          }} />
        ))}
      </div>

      <header className="App-header">
        <div className="header-glow"></div>
        <h1 className="car-title">
          <span className="title-icon">🚗</span>
          Car Price Predictor
        </h1>
        <p className="subtitle">AI-Powered Car Valuation System</p>
        
        <div className={`api-status ${apiStatus}`}>
          <div className="status-pulse"></div>
          {apiStatus === 'connected' ? '🟢 API Connected (85.4% Accuracy)' : 
           apiStatus === 'error' ? '🔴 API Error' : '🟡 Checking...'}
        </div>
      </header>

      <main className="App-main">
        <div className="container">
          <div className="glass-panel prediction-section">
            <PredictionForm 
              onPredict={handlePredict} 
              features={features}
              loading={loading}
            />
            
            {prediction && (
              <PredictionResult 
                result={prediction} 
                loading={loading}
              />
            )}
          </div>

          <div className="glass-panel dashboard-section">
            <Dashboard 
              predictionHistory={predictionHistory}
              currentPrediction={prediction}
            />
          </div>
        </div>
      </main>

      <footer className="App-footer">
        <p>Built with React & Flask | Car Price AI | Lasso Regression Model | © 2025</p>
        <p>Developed by Keerthan BM</p>
      </footer>
    </div>
  );
}

export default App;
