// Products.jsx - shows all tracked products with search

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { productService } from '../services/api';
import ProductCard from '../components/ProductCard';
import './Products.css';

export default function Products() {
  // state for products and filtering
  const [products, setProducts] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('');
  const nav = useNavigate();

  // load all products when page opens
  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const res = await productService.getAll();
      setProducts(res.data);
      setFiltered(res.data);
    } catch (e) {
      console.log('failed to load products', e);
    } finally {
      setLoading(false);
    }
  };

  // filter products based on search and category
  const handleFilter = () => {
    let result = products;
    
    if (searchTerm) {
      result = result.filter(p => 
        p.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (category) {
      result = result.filter(p => p.category === category);
    }
    
    setFiltered(result);
  };

  // get unique categories from products
  const categories = [...new Set(products.map(p => p.category))];

  return (
    <div className="products-page">
      <header className="products-header">
        <h1>Tracked Products</h1>
        <p>All products being tracked for price changes</p>
      </header>

      {/* filter bar */}
      <div className="filter-bar">
        <input
          type="text"
          placeholder="Filter by name..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setTimeout(handleFilter, 100);
          }}
        />
        <select
          value={category}
          onChange={(e) => {
            setCategory(e.target.value);
            setTimeout(handleFilter, 100);
          }}
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {/* products grid */}
      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="products-grid">
          {filtered.length > 0 ? (
            filtered.map(p => (
              <ProductCard
                key={p.id}
                product={p}
                onClick={() => nav(`/product/${p.id}`)}
              />
            ))
          ) : (
            <div className="no-results">
              <p>No products tracked yet</p>
              <p>Search for a product on the home page to start tracking prices</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
