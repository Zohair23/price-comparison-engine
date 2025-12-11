// App.jsx - main app component with routing
// BrowserRouter handles navigation between pages
// navbar is always visible, content changes based on route

import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-brand">pricecheck</Link>
          <div className="nav-links">
            <Link to="/">Search</Link>
            <Link to="/products">Tracked Products</Link>
          </div>
        </div>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/product/:productId" element={<ProductDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
