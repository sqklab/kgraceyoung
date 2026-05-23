'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ProductActions({ productId }: { productId: string }) {
  const [message, setMessage] = useState('');
  const token = () => localStorage.getItem('gy_customer_token') || '';

  async function addToCart() {
    const t = token();
    if (!t) { window.location.href = '/login'; return; }
    const res = await fetch(`${API}/api/v1/commerce/cart/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    setMessage(res.ok ? 'Added to cart' : 'Cart failed');
  }

  async function saveWishlist() {
    const t = token();
    if (!t) { window.location.href = '/login'; return; }
    const res = await fetch(`${API}/api/v1/commerce/wishlist/${productId}`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${t}` },
    });
    setMessage(res.ok ? 'Saved' : 'Wishlist failed');
  }

  return <div className="productActions"><button onClick={addToCart}>Add</button><button className="ghost" onClick={saveWishlist}>♡</button>{message && <small>{message}</small>}</div>;
}
