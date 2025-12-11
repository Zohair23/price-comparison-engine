// ProductDetail.jsx - shows one product with all its prices

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { productService, priceService } from '../services/api';
import PriceComparison from '../components/PriceComparison';
import PriceHistory from '../components/PriceHistory';
import PriceAlert from '../components/PriceAlert';
import './ProductDetail.css';

export default function ProductDetail() {
  // get the product id from the url (like /product/3)
  const { productId } = useParams();
  
  // store the product info and prices
  const [product, setProduct] = useState(null);
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  // runs when page opens, fetches product data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // get the product details
        const productRes = await productService.getById(productId);
        setProduct(productRes.data);

        // get prices from all retailers
        const pricesRes = await priceService.getComparison(productId);
        setPrices(pricesRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      fetchData();
    }
  }, [productId]);

  // show loading or error if needed
  if (loading) return <div className="loading">Loading...</div>;
  if (!product) return <div className="error">Product not found</div>;

  // the page layout
  return (
    <div className="product-detail">
      {/* product image and basic info */}
      <div className="detail-header">
        <img src={product.image_url} alt={product.name} className="detail-image" />
        <div className="detail-info">
          <h1>{product.name}</h1>
          <p className="category">{product.category}</p>
          <p className="description">{product.description}</p>
        </div>
      </div>

      {/* these are separate components for each section */}
      <PriceComparison prices={prices} />
      <PriceHistory productId={productId} />
      <PriceAlert productId={productId} />
    </div>
  );
}
