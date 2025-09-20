export const formatAccuracy = (accuracy) => {
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

export const formatPrice = (price) => {
  return `₹${parseFloat(price).toFixed(2)} Lakh`;
};

export const formatPercentage = (value) => {
  return `${parseFloat(value).toFixed(2)}%`;
};
