const express = require('express');
const router = express.Router();

// Mock database collection
const PRODUCTS = [
  { id: 1, name: 'Mechanical Keyboard', price: '79.99', stock: 12 }, // Notice: price returned as string!
  { id: 2, name: 'Wireless Mouse', price: '49.99', stock: 25 },
  { id: 3, name: 'Ultra-Wide Monitor', price: '349.99', stock: 5 },
];

router.get('/', (req, res) => {
  res.json({ products: PRODUCTS });
});

router.get('/:id', (req, res) => {
  const item = PRODUCTS.find((p) => p.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({ error: 'Product not found' });
  res.json(item);
});

module.exports = router;
