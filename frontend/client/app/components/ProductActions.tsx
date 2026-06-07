'use client';

import { useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GUEST_CART_KEY = 'gy_guest_cart';

type GuestCartItem = { product_id: string; quantity: number };

function readGuestCart(): GuestCartItem[] {
  try {
    const raw = localStorage.getItem(GUEST_CART_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeGuestCart(items: GuestCartItem[]) {
  localStorage.setItem(GUEST_CART_KEY, JSON.stringify(items));
  window.dispatchEvent(new Event('gy-cart-changed'));
}

export default function ProductActions({ productId, quantity = 1 }: { productId: string; quantity?: number }) {
  const [message, setMessage] = useState('');
  const token = () => localStorage.getItem('gy_customer_token') || '';

  async function addToCart() {
    const qty = Math.max(1, Math.min(99, Number(quantity || 1)));
    const t = token();
    if (!t) {
      const items = readGuestCart();
      const existing = items.find((item) => item.product_id === productId);
      if (existing) existing.quantity = Math.min(99, existing.quantity + qty);
      else items.push({ product_id: productId, quantity: qty });
      writeGuestCart(items);
      setMessage('Added to cart');
      return;
    }
    const res = await fetch(`${API}/api/v1/commerce/cart/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${t}` },
      body: JSON.stringify({ product_id: productId, quantity: qty }),
    });
    setMessage(res.ok ? 'Added to cart' : 'Cart failed');
    if (res.ok) window.dispatchEvent(new Event('gy-cart-changed'));
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

  return <div className="productActions"><button onClick={addToCart}>Add to Cart</button><button className="ghost" onClick={saveWishlist}>♡</button>{message && <small>{message}</small>}</div>;
}
