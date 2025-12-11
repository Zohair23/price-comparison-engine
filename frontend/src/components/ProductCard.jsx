// ProductCard.jsx - shows one product in a card format

import React, { useState } from 'react';
import './ProductCard.css';

export default function ProductCard({ product, onClick }) {
  const [imgError, setImgError] = useState(false);
  
  // fallback placeholder if image fails to load
  const placeholderImg = `https://placehold.co/200x200/f0f0f0/666?text=${encodeURIComponent(product.name.split(' ')[0])}`;
  
  // clicking the card takes you to the product detail page
  return (
    <div className="product-card" onClick={onClick}>
      {/* product image, or placeholder if none */}
      <img 
        src={imgError ? placeholderImg : (product.image_url || placeholderImg)} 
        alt={product.name}
        className="product-image"
        onError={() => setImgError(true)}
      />
      {/* product info */}
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="category">{product.category}</p>
      </div>
    </div>
  );
}
