import React from 'react';
import ProductList from './components/ProductList';

export default function App() {
  return (
    <div className="container">
      <header>
        <h1>Developer Hardware Store</h1>
      </header>
      <main>
        <ProductList />
      </main>
    </div>
  );
}
