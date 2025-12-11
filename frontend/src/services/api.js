// api.js - all backend api calls go through here
// uses axios, base url is /api (proxied to localhost:8000)

import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const productService = {
  getAll: () => api.get('/products/'),
  getTrending: () => api.get('/products/trending'),
  search: (query, category) => api.get('/products/search', { params: { q: query, category } }),
  searchAndAdd: (query) => api.post(`/products/search-add?q=${encodeURIComponent(query)}`),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products/', data)
};

export const priceService = {
  getComparison: (productId) => api.get(`/prices/comparison/${productId}`),
  getHistory: (productId, days = 30) => api.get(`/prices/history/${productId}`, { params: { days } }),
  getLowest: (productId) => api.get(`/prices/lowest/${productId}`),
  getBestDeal: (productId) => api.get(`/prices/best-deal/${productId}`)
};

export const alertService = {
  getAll: () => api.get('/alerts/'),
  create: (data) => api.post('/alerts/', data),
  check: () => api.post('/alerts/check'),
  deactivate: (id) => api.delete(`/alerts/${id}`)
};

export const recommendationService = {
  get: (productId) => api.get(`/recommendations/${productId}`),
  generate: (productId, limit = 5) => api.post(`/recommendations/generate/${productId}`, { limit })
};
