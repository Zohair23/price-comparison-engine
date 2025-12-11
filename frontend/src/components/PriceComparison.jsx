// PriceComparison.jsx - shows REAL prices from REAL stores

import React from 'react';
import './PriceComparison.css';

export default function PriceComparison({ prices }) {
  if (!prices || prices.length === 0) {
    return <div className="no-data">No price data available</div>;
  }

  // sort by price (lowest first)
  const sortedPrices = [...prices].sort((a, b) => a.price - b.price);
  const lowestPrice = sortedPrices[0].price;

  return (
    <div className="price-comparison">
      <h3>🏷️ Compare Prices</h3>
      <p className="subtitle">Real prices from real stores</p>
      
      <div className="price-list">
        {sortedPrices.map((price, idx) => (
          <div 
            key={idx} 
            className={`price-item ${price.price === lowestPrice ? 'best-price' : ''}`}
          >
            <div className="store-info">
              <span className="store-name">{price.retailer}</span>
              {price.price === lowestPrice && (
                <span className="best-badge">BEST PRICE</span>
              )}
            </div>
            
            <div className="price-info">
              <span className="price">${price.price.toFixed(2)}</span>
            </div>
            
            {price.url && (
              <a 
                href={price.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="buy-btn"
              >
                Buy Now →
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
