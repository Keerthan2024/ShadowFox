import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import "./Dashboard.css";

const Dashboard = ({ predictionHistory, currentPrediction }) => {
  // Prepare recent prices for chart
  const chartData = predictionHistory.slice(0, 10).map((h, idx) => ({
    index: predictionHistory.length - idx,
    price: h.prediction,
    ...h.input,
  })).reverse();

  const getCategory = (price) => {
    if (price >= 40) return "Luxury";
    if (price >= 25) return "High-End";
    if (price >= 15) return "Mid-Range";
    return "Budget";
  };

  return (
    <div className="dashboard">
      <h2>📊 Prediction Dashboard</h2>

      {/* Prediction History Table */}
      <div className="dashboard-history-section">
        <h3>Recent Predictions</h3>
        {predictionHistory.length === 0 ? (
          <p>No predictions yet.</p>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Date & Time</th>
                <th>Predicted Price ($K)</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {predictionHistory.map((h, idx) => (
                <tr key={h.id}>
                  <td>{predictionHistory.length - idx}</td>
                  <td>{h.timestamp}</td>
                  <td>{h.prediction.toFixed(1)}</td>
                  <td>{getCategory(h.prediction)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Prediction History Chart */}
      {chartData.length >= 2 && (
        <div className="dashboard-chart-section">
          <h3>Prediction Trend (Last {chartData.length})</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" label={{ value: "Prediction#", position: "insideBottomRight", dy: 8 }} />
              <YAxis label={{ value: "Price ($K)", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="price" fill="#764ba2" name="Predicted Price" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Current Prediction Details */}
      {currentPrediction && !currentPrediction.error && (
        <div className="dashboard-current-section">
          <h3>Latest Prediction</h3>
          <ul>
            <li><b>Predicted Price:</b> ${currentPrediction.prediction.toFixed(1)}K</li>
            <li><b>Category:</b> {getCategory(currentPrediction.prediction)}</li>
            <li><b>Model Accuracy:</b> {currentPrediction.accuracy || "91.79%"} </li>
            <li><b>Confidence:</b> {currentPrediction.confidence}% </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
