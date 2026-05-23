'use client';

import { useEffect, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Cart = { id: string; subtotal: string; item_count: number; items: { id: string; quantity: number; line_total: string; product: { name: string; brand?: string; image_url?: string; price: string; currency: string } }[] };

export default function CartPage() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [message, setMessage] = useState('Loading cart...');
  const token = () => localStorage.getItem('gy_customer_token') || '';

  async function load() {
    const t = token();
    if (!t) { window.location.href = '/login'; return; }
    const res = await fetch(`${API}/api/v1/commerce/cart`, { headers: { Authorization: `Bearer ${t}` } });
    const json = await res.json();
    if (!res.ok) throw new Error(json.detail || 'Cart unavailable');
    setCart(json); setMessage('');
  }

  async function updateItem(id: string, quantity: number) {
    const res = await fetch(`${API}/api/v1/commerce/cart/items/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify({ quantity }) });
    const json = await res.json();
    if (!res.ok) { setMessage(json.detail || 'Update failed'); return; }
    setCart(json);
  }

  useEffect(() => { load().catch((e) => setMessage(String(e))); }, []);

  return <main className="commercePage"><a href="/">← Grace Young</a><h1>Your Cart</h1>{message && <div className="authNotice">{message}</div>}{cart && <><div className="cartList">{cart.items.length === 0 ? <p>Your cart is empty.</p> : cart.items.map((i) => <article className="cartItem" key={i.id}>{i.product.image_url && <img src={i.product.image_url} alt={i.product.name} />}<div><strong>{i.product.name}</strong><span>{i.product.brand}</span><span>${Number(i.product.price).toFixed(2)}</span></div><div className="qty"><button onClick={() => updateItem(i.id, Math.max(0, i.quantity - 1))}>−</button><b>{i.quantity}</b><button onClick={() => updateItem(i.id, i.quantity + 1)}>+</button></div><b>${Number(i.line_total).toFixed(2)}</b></article>)}</div><section className="summary"><p>Items: {cart.item_count}</p><h2>Subtotal ${Number(cart.subtotal).toFixed(2)}</h2><a className="primaryLink" href="/checkout">Checkout</a></section></>}</main>;
}
