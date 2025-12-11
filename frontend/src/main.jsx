// main.jsx - entry point for the react app
// this file loads the App component into the html page

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'

// finds the div with id="root" in index.html and puts our app there
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
