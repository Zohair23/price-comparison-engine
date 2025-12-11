// Home.jsx - main page with search and trending products from eBay

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { productService } from '../services/api';
import ProductCard from '../components/ProductCard';
import './Home.css';

export default function Home() {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingTrending, setLoadingTrending] = useState(true);
  const [searched, setSearched] = useState(false);
  const nav = useNavigate();

  // load trending products on page load
  useEffect(() => {
    loadTrending();
  }, []);

  const loadTrending = async () => {
    setLoadingTrending(true);
    try {
      const res = await productService.getTrending();
      setTrending(res.data);
    } catch (err) {
      console.log('Failed to load trending', err);
    } finally {
      setLoadingTrending(false);
    }
  };

  // search eBay when user submits
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchTerm.trim()) return;

    setLoading(true);
    setSearched(true);
    
    try {
      const res = await productService.searchAndAdd(searchTerm);
      setResults(res.data);
    } catch (err) {
      console.log('Search failed', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // clear search and go back to trending
  const clearSearch = () => {
    setSearched(false);
    setResults([]);
    setSearchTerm('');
  };

  return (
    <div className="home">
      {/* search bar - Amazon style */}
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search eBay products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? '...' : 'Search'}
          </button>
        </form>
      </div>

      {/* show search results or trending */}
      {searched ? (
        <section className="results-section">
          <div className="section-header">
            <h2>Results for "{searchTerm}"</h2>
            <button onClick={clearSearch} className="clear-btn">
              ← Back to Trending
            </button>
          </div>

          {loading ? (
            <div className="loading">Searching eBay...</div>
          ) : results.length > 0 ? (
            <div className="products-grid">
              {results.map(p => (
                <ProductCard
                  key={p.id}
                  product={p}
                  onClick={() => nav(`/product/${p.id}`)}
                />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <p>No products found for "{searchTerm}"</p>
              <p>Try a different search term</p>
            </div>
          )}
        </section>
      ) : (
        <section className="trending-section">
          <div className="section-header">
            <h2>🔥 Trending on eBay</h2>
          </div>

          {loadingTrending ? (
            <div className="loading">Loading trending products...</div>
          ) : trending.length > 0 ? (
            <div className="products-grid">
              {trending.map(p => (
                <ProductCard
                  key={p.id}
                  product={p}
                  onClick={() => nav(`/product/${p.id}`)}
                />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <p>Loading trending products...</p>
              <button onClick={loadTrending} className="retry-btn">
                Retry
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
