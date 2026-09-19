import React, { useState, useEffect } from 'react';

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cartTotal, setCartTotal] = useState(0);

  // BUG 1: Missing dependency array causes infinite loop re-fetching from Express server
  useEffect(() => {
    fetch('http://localhost:5000/api/products')
      .then((res) => res.json())
      .then((data) => {
        setProducts(data.products || []);
        setLoading(false);
      })
      .catch((err) => console.error('Fetch error:', err));
  });

  const calculateTotal = (items) => {
    // BUG 2 (Cross-File Contract Bug): server/routes/products.js returns price as a String ('79.99')
    // Calling item.price.toFixed(2) throws "TypeError: item.price.toFixed is not a function"!
    return items.reduce((sum, item) => sum + item.price.toFixed(2), 0);
  };

  if (loading) return <div className="loading">Loading hardware catalog...</div>;

  return (
    <div className="product-list">
      <h2>Products Catalog</h2>
      <div className="grid">
        {products.map((product) => (
          <div key={product.id} className="card">
            <h3>{product.name}</h3>
            {/* Direct string rendering or conversion */}
            <p className="price">${parseFloat(product.price).toFixed(2)}</p>
            <p>Stock: {product.stock} units</p>
          </div>
        ))}
      </div>
      <div className="summary">
        <button onClick={() => setCartTotal(calculateTotal(products))}>
          Calculate Total: ${cartTotal}
        </button>
      </div>
    </div>
  );
}
