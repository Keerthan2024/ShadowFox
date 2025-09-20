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
      const response = await axios.get('/api/health');
      setApiStatus(response.data.model_loaded ? 'connected' : 'error');
    } catch (error) {
      setApiStatus('error');
      console.error('API health check failed:', error);
    }
  };

  const loadFeatures = async () => {
    try {
      const response = await axios.get('/api/features');
      setFeatures(response.data.features);
    } catch (error) {
      console.error('Failed to load features:', error);
    }
  };

  const handlePredict = async (formData) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/predict', formData);
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
    <div className="App dark-theme">
      {/* Animated background */}
      <div className="background-particles">
        {[...Array(30)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 10}s`
          }} />
        ))}
      </div>

      <header className="App-header">
        <div className="header-glow"></div>
        <h1 className="neon-title">
          <span className="title-icon">🏠</span>
          Boston House Price Predictor
        </h1>
        <p className="subtitle-neon">AI-Powered Real Estate Price Prediction</p>
        
        <div className={`api-status-neon ${apiStatus}`}>
          <div className="status-pulse"></div>
          {apiStatus === 'connected' ? 'API Connected' : 
           apiStatus === 'error' ? 'API Error' : ' Checking...'}
        </div>
      </header>

      <main className="App-main">
        <div className="container-dark">
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

      <footer className="App-footer-dark">
        <div className="footer-glow"></div>
        <p>Built with React & Flask | Model Accuracy: 91.79% | © 2025</p>
        <p>Developed by Keerthan B M</p>
      </footer>
    </div>
  );
}

export default App;
