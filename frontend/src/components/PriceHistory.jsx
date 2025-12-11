// PriceHistory.jsx - shows how prices changed over time

import React, { useState, useEffect } from 'react';
import { priceService } from '../services/api';
import './PriceHistory.css';

export default function PriceHistory({ productId }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // get price history when page loads
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // get last 30 days of prices
        const response = await priceService.getHistory(productId, 30);
        setHistory(response.data);
      } catch (error) {
        console.error('Error fetching price history:', error);
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      fetchHistory();
    }
  }, [productId]);

  if (loading) return <div className="no-data">Loading history...</div>;
  if (!history || history.length === 0) {
    return <div className="no-data">No price history available</div>;
  }

  // organise prices by retailer so each store has its own chart
  const byRetailer = {};
  history.forEach(h => {
    if (!byRetailer[h.retailer]) byRetailer[h.retailer] = [];
    byRetailer[h.retailer].push(h);
  });

  return (
    <div className="price-history">
      <h3>30-Day Price History</h3>
      <div className="history-retailers">
        {/* show a mini chart for each retailer */}
        {Object.entries(byRetailer).map(([retailer, prices]) => (
          <div key={retailer} className="retailer-history">
            <h4>{retailer}</h4>
            <div className="mini-chart">
              {/* each bar represents a day's price */}
              {prices.slice(0, 10).map((p, idx) => {
                const min = Math.min(...prices.map(x => x.price));
                const max = Math.max(...prices.map(x => x.price));
                const range = max - min || 1;
                const height = ((p.price - min) / range) * 100;
                return (
                  <div
                    key={idx}
                    className="chart-bar"
                    style={{ height: `${height + 10}%` }}
                    title={`$${p.price.toFixed(2)}`}
                  ></div>
                );
              })}
            </div>
            <p className="price-range">${Math.min(...prices.map(p => p.price)).toFixed(2)} - ${Math.max(...prices.map(p => p.price)).toFixed(2)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
