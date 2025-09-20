import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter, Area, AreaChart
} from 'recharts';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = ({ predictionHistory, currentPrediction }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [activeChart, setActiveChart] = useState('trends');
  const [modelStats, setModelStats] = useState(null);

  // Colors for charts
  const COLORS = ['#00D4FF', '#FF4DA6', '#4CAF50', '#FFC107', '#9C27B0', '#FF5722', '#E91E63', '#607D8B'];

  // Utility function to format accuracy consistently
  const formatAccuracy = (accuracy) => {
    if (typeof accuracy === 'string') {
      // Extract number from string like "85.4%" 
      const match = accuracy.match(/(\d+\.?\d*)/);
      if (match) {
        return `${parseFloat(match[1]).toFixed(2)}%`;
      }
      return accuracy;
    }
    
    if (typeof accuracy === 'number') {
      return `${accuracy.toFixed(2)}%`;
    }
    
    return '85.35%'; // Default fallback
  };

  useEffect(() => {
    if (predictionHistory.length > 0) {
      generateAnalysisData();
    }
    fetchModelStats();
  }, [predictionHistory]);

  const fetchModelStats = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/model-info');
      setModelStats(response.data);
      console.log('Model stats loaded:', response.data);
    } catch (error) {
      console.error('Failed to fetch model stats:', error);
    }
  };

  const generateAnalysisData = () => {
    if (predictionHistory.length === 0) return;

    // Price Trends Over Time (Last 15 predictions)
    const trendData = predictionHistory
      .slice(0, 15)
      .reverse()
      .map((item, index) => ({
        prediction: index + 1,
        price: parseFloat(item.prediction),
        timestamp: new Date(item.timestamp).toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit' 
        }),
        carModel: item.input.car_name || 'Unknown',
        year: item.input.year || 2018
      }));

    // Price Distribution by Categories
    const priceCategories = predictionHistory.reduce((acc, item) => {
      const price = parseFloat(item.prediction);
      let category;
      if (price < 3) category = 'Budget (< ₹3L)';
      else if (price < 8) category = 'Mid-Range (₹3-8L)';
      else if (price < 15) category = 'Premium (₹8-15L)';
      else category = 'Luxury (₹15L+)';
      
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {});

    const categoryData = Object.entries(priceCategories).map(([name, value]) => ({
      name: name.split(' ')[0], // Shorter names for mobile
      fullName: name,
      value,
      percentage: ((value / predictionHistory.length) * 100).toFixed(1)
    }));

    // Car Model Analysis (Top 8 most predicted)
    const modelAnalysis = predictionHistory.reduce((acc, item) => {
      const model = (item.input.car_name || 'Unknown').toLowerCase();
      const price = parseFloat(item.prediction);
      
      if (!acc[model]) {
        acc[model] = { model, totalPrice: 0, count: 0, avgPrice: 0, prices: [] };
      }
      acc[model].totalPrice += price;
      acc[model].count += 1;
      acc[model].avgPrice = acc[model].totalPrice / acc[model].count;
      acc[model].prices.push(price);
      
      return acc;
    }, {});

    const modelData = Object.values(modelAnalysis)
      .sort((a, b) => b.count - a.count) // Sort by frequency
      .slice(0, 8)
      .map(item => ({
        model: item.model.charAt(0).toUpperCase() + item.model.slice(1),
        avgPrice: parseFloat(item.avgPrice.toFixed(2)),
        predictions: item.count,
        minPrice: Math.min(...item.prices),
        maxPrice: Math.max(...item.prices)
      }));

    // Year vs Price Analysis
    const yearAnalysis = predictionHistory.reduce((acc, item) => {
      const year = item.input.year || 2018;
      const price = parseFloat(item.prediction);
      const age = 2024 - year;
      
      if (!acc[year]) {
        acc[year] = { year, age, totalPrice: 0, count: 0, avgPrice: 0 };
      }
      acc[year].totalPrice += price;
      acc[year].count += 1;
      acc[year].avgPrice = acc[year].totalPrice / acc[year].count;
      
      return acc;
    }, {});

    const yearData = Object.values(yearAnalysis)
      .sort((a, b) => a.year - b.year)
      .map(item => ({
        year: item.year,
        age: item.age,
        avgPrice: parseFloat(item.avgPrice.toFixed(2)),
        count: item.count
      }));

    // Fuel Type Analysis
    const fuelAnalysis = predictionHistory.reduce((acc, item) => {
      const fuel = item.input.fuel_type || 'Unknown';
      const price = parseFloat(item.prediction);
      
      if (!acc[fuel]) {
        acc[fuel] = { fuel, totalPrice: 0, count: 0, avgPrice: 0 };
      }
      acc[fuel].totalPrice += price;
      acc[fuel].count += 1;
      acc[fuel].avgPrice = acc[fuel].totalPrice / acc[fuel].count;
      
      return acc;
    }, {});

    const fuelData = Object.values(fuelAnalysis).map(item => ({
      fuel: item.fuel,
      avgPrice: parseFloat(item.avgPrice.toFixed(2)),
      count: item.count,
      percentage: ((item.count / predictionHistory.length) * 100).toFixed(1)
    }));

    setAnalysisData({
      trends: trendData,
      categories: categoryData,
      models: modelData,
      years: yearData,
      fuels: fuelData
    });
  };

  const calculateStats = () => {
    if (predictionHistory.length === 0) return null;
    
    const prices = predictionHistory.map(item => parseFloat(item.prediction));
    const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const recentTrend = predictionHistory.length >= 2 ? 
      (prices[0] - prices[1] > 0 ? 'up' : prices[0] - prices[1] < 0 ? 'down' : 'stable') : 'stable';
    
    return { avgPrice, maxPrice, minPrice, recentTrend };
  };

  const stats = calculateStats();

  return (
    <div className="dashboard">
      <h2>📊 Car Price Analytics Dashboard</h2>
      
      {/* Model Performance Info */}
      {modelStats && (
        <div className="model-info-section">
          <h4>🤖 AI Model Information</h4>
          <div className="model-stats">
            <div className="model-stat">
              <span className="stat-value">{modelStats.model_name || 'Lasso Regression'}</span>
              <span className="stat-label">Model Type</span>
            </div>
            <div className="model-stat">
              <span className="stat-value">
                {formatAccuracy(modelStats.accuracy || '85.35%')}
              </span>
              <span className="stat-label">Accuracy</span>
            </div>
            <div className="model-stat">
              <span className="stat-value">{modelStats.feature_count || 10}</span>
              <span className="stat-label">Features</span>
            </div>
            <div className="model-stat">
              <span className="stat-value">{modelStats.training_samples || 239}</span>
              <span className="stat-label">Training Data</span>
            </div>
          </div>
        </div>
      )}

      {/* Current Prediction Stats */}
      {currentPrediction && !currentPrediction.error && (
        <div className="dashboard-current-section">
          <h4>🎯 Latest Prediction Analysis</h4>
          <div className="current-stats">
            <div className="stat-item highlight">
              <span className="stat-value">₹{currentPrediction.prediction}</span>
              <span className="stat-label">Predicted Price</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{currentPrediction.confidence}%</span>
              <span className="stat-label">Confidence</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {formatAccuracy(currentPrediction.model_accuracy || '85.35%')}
              </span>
              <span className="stat-label">Model Accuracy</span>
            </div>
            {stats && (
              <div className="stat-item">
                <span className={`stat-value trend-${stats.recentTrend}`}>
                  {stats.recentTrend === 'up' ? '📈' : stats.recentTrend === 'down' ? '📉' : '➡️'}
                </span>
                <span className="stat-label">Recent Trend</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chart Navigation */}
      {predictionHistory.length >= 2 && analysisData && (
        <>
          <div className="chart-nav">
            <button 
              className={`nav-btn ${activeChart === 'trends' ? 'active' : ''}`}
              onClick={() => setActiveChart('trends')}
            >
              📈 Price Trends
            </button>
            <button 
              className={`nav-btn ${activeChart === 'categories' ? 'active' : ''}`}
              onClick={() => setActiveChart('categories')}
            >
              🥧 Categories
            </button>
            <button 
              className={`nav-btn ${activeChart === 'models' ? 'active' : ''}`}
              onClick={() => setActiveChart('models')}
            >
              🚗 Car Models
            </button>
            <button 
              className={`nav-btn ${activeChart === 'years' ? 'active' : ''}`}
              onClick={() => setActiveChart('years')}
            >
              📅 Year Analysis
            </button>
            <button 
              className={`nav-btn ${activeChart === 'fuels' ? 'active' : ''}`}
              onClick={() => setActiveChart('fuels')}
            >
              ⛽ Fuel Types
            </button>
          </div>

          {/* Chart Container */}
          <div className="chart-container">
            {/* Price Trends Chart */}
            {activeChart === 'trends' && (
              <div className="chart-section">
                <h4>📈 Price Prediction Trends (Last 15 Predictions)</h4>
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={analysisData.trends}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00D4FF" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#00D4FF" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      dataKey="prediction" 
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis 
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(0,0,0,0.9)', 
                        border: '1px solid #00D4FF',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value, name) => [`₹${value} Lakh`, 'Predicted Price']}
                      labelFormatter={(label) => `Prediction #${label}`}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="price" 
                      stroke="#00D4FF" 
                      strokeWidth={3}
                      fill="url(#priceGradient)"
                      dot={{ fill: '#00D4FF', strokeWidth: 2, r: 4 }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Price Categories Chart */}
            {activeChart === 'categories' && (
              <div className="chart-section">
                <h4>🥧 Price Category Distribution</h4>
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={analysisData.categories}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {analysisData.categories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(0,0,0,0.9)', 
                        border: '1px solid #00D4FF',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value, name) => [value, 'Predictions']}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Car Models Analysis */}
            {activeChart === 'models' && (
              <div className="chart-section">
                <h4>🚗 Average Price by Car Model (Most Predicted)</h4>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={analysisData.models}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      dataKey="model" 
                      stroke="#8A8D91"
                      tick={{ fontSize: 10 }}
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis 
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Avg Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(0,0,0,0.9)', 
                        border: '1px solid #00D4FF',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value, name) => [
                        name === 'avgPrice' ? `₹${value} Lakh` : value,
                        name === 'avgPrice' ? 'Average Price' : 'Predictions'
                      ]}
                    />
                    <Bar 
                      dataKey="avgPrice" 
                      fill="#FF4DA6"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Year Analysis Chart */}
            {activeChart === 'years' && (
              <div className="chart-section">
                <h4>📅 Price vs Manufacturing Year</h4>
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart data={analysisData.years}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      type="number"
                      dataKey="year" 
                      domain={['dataMin - 1', 'dataMax + 1']}
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis 
                      type="number"
                      dataKey="avgPrice"
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Avg Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      cursor={{ strokeDasharray: '3 3' }}
                      contentStyle={{ 
                        backgroundColor: 'rgba(0,0,0,0.9)', 
                        border: '1px solid #00D4FF',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value, name) => [
                        name === 'avgPrice' ? `₹${value} Lakh` : value,
                        name === 'avgPrice' ? 'Average Price' : 'Count'
                      ]}
                    />
                    <Scatter 
                      name="Price vs Year" 
                      dataKey="avgPrice" 
                      fill="#4CAF50"
                    />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Fuel Types Analysis */}
            {activeChart === 'fuels' && (
              <div className="chart-section">
                <h4>⛽ Average Price by Fuel Type</h4>
                <ResponsiveContainer width="100%" height={350}>
                  <BarChart data={analysisData.fuels}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis 
                      dataKey="fuel" 
                      stroke="#8A8D91"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis 
                      stroke="#8A8D91"
                      tick={{ fontSize: 11 }}
                      label={{ value: 'Avg Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'rgba(0,0,0,0.9)', 
                        border: '1px solid #00D4FF',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value, name) => [
                        name === 'avgPrice' ? `₹${value} Lakh` : value,
                        name === 'avgPrice' ? 'Average Price' : 'Count'
                      ]}
                    />
                    <Bar 
                      dataKey="avgPrice" 
                      fill="#9C27B0"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </>
      )}

      {/* Overall Statistics */}
      {stats && (
        <div className="dashboard-stats">
          <h4>📊 Overall Statistics</h4>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">{predictionHistory.length}</span>
              <span className="stat-text">Total Predictions</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">₹{stats.avgPrice.toFixed(1)}</span>
              <span className="stat-text">Average Price</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">₹{stats.maxPrice}</span>
              <span className="stat-text">Highest Price</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">₹{stats.minPrice}</span>
              <span className="stat-text">Lowest Price</span>
            </div>
          </div>
        </div>
      )}

      {/* Prediction History */}
      <div className="dashboard-history-section">
        <h4>📋 Recent Predictions</h4>
        
        {predictionHistory.length === 0 ? (
          <div className="history-empty">
            <p>📊 No predictions yet!</p>
            <p>Use the form to make your first car price prediction and see beautiful analytics.</p>
          </div>
        ) : (
          <div className="history-list">
            {predictionHistory.slice(0, 6).map((item, idx) => (
              <div 
                key={item.id} 
                className={`history-item ${idx === 0 ? 'new-item' : ''}`}
              >
                <div className="history-header">
                  <span className="history-price">₹{item.prediction} Lakh</span>
                  <span className="history-timestamp">{item.timestamp}</span>
                </div>
                <div className="history-details">
                  <span className="history-detail-item">
                    🚗 {item.input.car_name || 'Unknown'}
                  </span>
                  <span className="history-detail-item">
                    📅 {item.input.year || '----'}
                  </span>
                  <span className="history-detail-item">
                    ⛽ {item.input.fuel_type || 'Unknown'}
                  </span>
                  <span className="history-detail-item">
                    📏 {item.input.kms_driven ? `${item.input.kms_driven.toLocaleString()} km` : 'Unknown km'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Empty State for Charts */}
      {predictionHistory.length < 2 && (
        <div className="charts-empty-state">
          <div className="empty-chart-placeholder">
            <h4>📈 Interactive Charts Coming Soon!</h4>
            <p>Make 2 or more predictions to unlock:</p>
            <ul>
              <li>📈 Price trend analysis</li>
              <li>🥧 Category distribution</li>
              <li>🚗 Car model comparisons</li>
              <li>📅 Year-based insights</li>
              <li>⛽ Fuel type analysis</li>
            </ul>
            <p className="encouragement">Start predicting to see your data come alive! 🚀</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
