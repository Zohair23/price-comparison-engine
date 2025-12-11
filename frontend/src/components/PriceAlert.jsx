// PriceAlert.jsx - form to set price alerts
// user enters target price, gets notified when price drops

import React, { useState, useEffect } from 'react';
import { alertService, priceService } from '../services/api';
import './PriceAlert.css';

export default function PriceAlert({ productId, onAlertCreated }) {
  // form data and existing alerts
  const [threshold, setThreshold] = useState('');
  const [retailer, setRetailer] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(null);

  // load alerts and current price when page opens
  useEffect(() => {
    fetchAlerts();
    fetchCurrentPrice();
  }, [productId]);

  // get all alerts from database
  const fetchAlerts = async () => {
    try {
      const response = await alertService.getAll();
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  // get the lowest current price to show user
  const fetchCurrentPrice = async () => {
    try {
      const response = await priceService.getLowest(productId);
      setCurrentPrice(response.data.price);
    } catch (error) {
      console.error('Error fetching current price:', error);
    }
  };

  // when user submits the form
  const handleCreateAlert = async (e) => {
    e.preventDefault();
    try {
      await alertService.create({
        product_id: productId,
        price_threshold: parseFloat(threshold),
        target_retailer: retailer || null
      });
      // clear form and reload alerts
      setThreshold('');
      setRetailer('');
      fetchAlerts();
      onAlertCreated?.();
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  // when user deletes an alert
  const handleDeleteAlert = async (alertId) => {
    try {
      await alertService.deactivate(alertId);
      fetchAlerts();
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  return (
    <div className="price-alert">
      <h3>Price Alerts</h3>
      {currentPrice && <p className="current-price">Current lowest: ${currentPrice.toFixed(2)}</p>}
      
      {/* form to create new alert */}
      <form onSubmit={handleCreateAlert} className="alert-form">
        <input
          type="number"
          step="0.01"
          placeholder="Alert when price drops to..."
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Retailer (optional)"
          value={retailer}
          onChange={(e) => setRetailer(e.target.value)}
        />
        <button type="submit">Create Alert</button>
      </form>

      {/* list of existing alerts */}
      {alerts.length > 0 && (
        <div className="alerts-list">
          <h4>Your Alerts</h4>
          {alerts.map((alert) => (
            <div key={alert.id} className={`alert-item ${alert.triggered ? 'triggered' : ''}`}>
              <div className="alert-info">
                <span className="threshold">${alert.price_threshold.toFixed(2)}</span>
                {alert.target_retailer && <span className="retailer">{alert.target_retailer}</span>}
                {alert.triggered && <span className="badge">Triggered!</span>}
              </div>
              <button
                className="delete-btn"
                onClick={() => handleDeleteAlert(alert.id)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
