// SearchBar.jsx - the search form at the top of the page

import React, { useState, useEffect } from 'react';
import { productService, priceService } from '../services/api';
import './SearchBar.css';

export default function SearchBar({ onSearch }) {
  // store what user types
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');

  // when form is submitted, call the search function from parent
  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(query, category);
  };

  return (
    <form className="search-bar" onSubmit={handleSearch}>
      {/* text input for product name */}
      <input
        type="text"
        placeholder="Search products..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="search-input"
      />
      {/* optional category filter */}
      <input
        type="text"
        placeholder="Category (optional)"
        value={category}
        onChange={(e) => setCategory(e.target.value)}
        className="category-input"
      />
      <button type="submit" className="search-btn">Search</button>
    </form>
  );
}
