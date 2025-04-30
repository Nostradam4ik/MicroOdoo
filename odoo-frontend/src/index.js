import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // Styles globaux
import App from './App'; // Composant principal
import reportWebVitals from './reportWebVitals'; // Outil de mesure de performance
import 'bootstrap/dist/css/bootstrap.min.css'; // Intégration Bootstrap

// Création de la racine de l'application
const root = ReactDOM.createRoot(document.getElementById('root'));

// Rendu du composant racine dans un mode strict pour détecter les problèmes potentiels
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Mesure des performances (facultatif, utilisé pour le debug ou analytics)
reportWebVitals();