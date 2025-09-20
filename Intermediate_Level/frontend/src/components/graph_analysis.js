import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, ScatterChart, Scatter
} from 'recharts';
import axios from 'axios';
import './GraphAnalysis.css';

const GraphAnalysis = ({ predictionHistory, currentPrediction }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeChart, setActiveChart] = useState('trends');

  // Colors for charts
  const COLORS = ['#00D4FF', '#FF4DA6', '#4CAF50', '#FFC107', '#9C27B0', '#FF5722'];

  useEffect(() => {
    if (predictionHistory.length > 0) {
      generateAnalysisData();
    }
  }, [predictionHistory]);

  const generateAnalysisData = () => {
    if (predictionHistory.length === 0) return;

    // Price Trends Over Time
    const trendData = predictionHistory
      .slice(0, 10)
      .reverse()
      .map((item, index) => ({
        prediction: index + 1,
        price: parseFloat(item.prediction),
        timestamp: new Date(item.timestamp).toLocaleTimeString(),
        carModel: item.input.car_name || 'Unknown'
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
      name,
      value,
      percentage: ((value / predictionHistory.length) * 100).toFixed(1)
    }));

    // Car Model Analysis
    const modelAnalysis = predictionHistory.reduce((acc, item) => {
      const model = item.input.car_name || 'Unknown';
      const price = parseFloat(item.prediction);
      
      if (!acc[model]) {
        acc[model] = { model, totalPrice: 0, count: 0, avgPrice: 0 };
      }
      acc[model].totalPrice += price;
      acc[model].count += 1;
      acc[model].avgPrice = acc[model].totalPrice / acc[model].count;
      
      return acc;
    }, {});

    const modelData = Object.values(modelAnalysis)
      .sort((a, b) => b.avgPrice - a.avgPrice)
      .slice(0, 8)
      .map(item => ({
        model: item.model.charAt(0).toUpperCase() + item.model.slice(1),
        avgPrice: parseFloat(item.avgPrice.toFixed(2)),
        predictions: item.count
      }));

    // Year vs Price Analysis
    const yearAnalysis = predictionHistory.reduce((acc, item) => {
      const year = item.input.year || 2018;
      const price = parseFloat(item.prediction);
      
      if (!acc[year]) {
        acc[year] = { year, totalPrice: 0, count: 0, avgPrice: 0 };
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
        avgPrice: parseFloat(item.avgPrice.toFixed(2)),
        count: item.count
      }));

    setAnalysisData({
      trends: trendData,
      categories: categoryData,
      models: modelData,
      years: yearData
    });
  };

  const fetchModelStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/model-info');
      // You can use this data for additional insights
    } catch (error) {
      console.error('Failed to fetch model stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!analysisData || predictionHistory.length < 2) {
    return (
      <div className="graph-analysis">
        <h3>📊 Graph Analysis</h3>
        <div className="no-data">
          <p>📈 Make more predictions to see analysis graphs!</p>
          <p>Need at least 2 predictions for meaningful insights.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="graph-analysis">
      <h3>📊 Price Analysis Dashboard</h3>
      
      {/* Chart Navigation */}
      <div className="chart-nav">
        <button 
          className={`nav-btn ${activeChart === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveChart('trends')}
        >
          📈 Trends
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
          🚗 Models
        </button>
        <button 
          className={`nav-btn ${activeChart === 'years' ? 'active' : ''}`}
          onClick={() => setActiveChart('years')}
        >
          📅 Years
        </button>
      </div>

      {/* Chart Container */}
      <div className="chart-container">
        {/* Price Trends Chart */}
        {activeChart === 'trends' && (
          <div className="chart-section">
            <h4>📈 Price Prediction Trends</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analysisData.trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="prediction" 
                  stroke="#8A8D91"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  stroke="#8A8D91"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Price (₹ Lakh)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid #00D4FF',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                  formatter={(value) => [`₹${value} Lakh`, 'Predicted Price']}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#00D4FF" 
                  strokeWidth={3}
                  dot={{ fill: '#00D4FF', strokeWidth: 2, r: 5 }}
                  name="Predicted Price"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Price Categories Chart */}
        {activeChart === 'categories' && (
          <div className="chart-section">
            <h4>🥧 Price Category Distribution</h4>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analysisData.categories}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {analysisData.categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid #00D4FF',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Car Models Analysis */}
        {activeChart === 'models' && (
          <div className="chart-section">
            <h4>🚗 Average Price by Car Model</h4>
            <ResponsiveContainer width="100%" height={300}>
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
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Avg Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
                    border: '1px solid #00D4FF',
                    borderRadius: '8px',
                    color: 'white'
                  }}
                  formatter={(value) => [`₹${value} Lakh`, 'Average Price']}
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
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart data={analysisData.years}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  type="number"
                  dataKey="year" 
                  domain={['dataMin - 1', 'dataMax + 1']}
                  stroke="#8A8D91"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  type="number"
                  dataKey="avgPrice"
                  stroke="#8A8D91"
                  tick={{ fontSize: 12 }}
                  label={{ value: 'Avg Price (₹ Lakh)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ 
                    backgroundColor: 'rgba(0,0,0,0.8)', 
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
      </div>

      {/* Statistics Summary */}
      <div className="stats-summary">
        <div className="stat-card">
          <span className="stat-number">{predictionHistory.length}</span>
          <span className="stat-label">Total Predictions</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            ₹{(predictionHistory.reduce((sum, item) => sum + parseFloat(item.prediction), 0) / predictionHistory.length).toFixed(1)}
          </span>
          <span className="stat-label">Average Price</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            ₹{Math.max(...predictionHistory.map(item => parseFloat(item.prediction))).toFixed(1)}
          </span>
          <span className="stat-label">Highest Price</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">
            ₹{Math.min(...predictionHistory.map(item => parseFloat(item.prediction))).toFixed(1)}
          </span>
          <span className="stat-label">Lowest Price</span>
        </div>
      </div>
    </div>
  );
};

export default GraphAnalysis;
