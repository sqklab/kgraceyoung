'use client';

import { useEffect, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Wish = { id: string; product_id: string; product: { name: string; brand?: string; image_url?: string; price: string } };

export default function WishlistPage() {
  const [items, setItems] = useState<Wish[]>([]);
  const [message, setMessage] = useState('Loading wishlist...');
  const token = () => localStorage.getItem('gy_customer_token') || '';
  async function load() { const t = token(); if (!t) { window.location.href = '/login'; return; } const res = await fetch(`${API}/api/v1/commerce/wishlist`, { headers: { Authorization: `Bearer ${t}` } }); const json = await res.json(); if (!res.ok) throw new Error(json.detail || 'Wishlist unavailable'); setItems(json); setMessage(''); }
  async function remove(productId: string) { const res = await fetch(`${API}/api/v1/commerce/wishlist/${productId}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token()}` } }); setItems(await res.json()); }
  async function addToCart(productId: string) { await fetch(`${API}/api/v1/commerce/cart/items`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify({ product_id: productId, quantity: 1 }) }); setMessage('Added to cart'); }
  useEffect(() => { load().catch((e) => setMessage(String(e))); }, []);
  return <main className="commercePage"><a href="/">← Grace Young</a><h1>Wishlist</h1>{message && <div className="authNotice">{message}</div>}<div className="products">{items.length === 0 ? <article className="tile">No wishlist items yet<span>Save products from the homepage.</span></article> : items.map((i) => <article className="product" key={i.id}>{i.product.image_url && <img src={i.product.image_url} alt={i.product.name} />}<small>{i.product.brand}</small><strong>{i.product.name}</strong><span>${Number(i.product.price).toFixed(2)}</span><div className="productActions"><button onClick={() => addToCart(i.product_id)}>Add</button><button className="ghost" onClick={() => remove(i.product_id)}>Remove</button></div></article>)}</div></main>;
}
