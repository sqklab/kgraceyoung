'use client';

import { useEffect, useMemo, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const GUEST_CART_KEY = 'gy_guest_cart';

type Product = { id: string; slug: string; name: string; brand?: string; image_url?: string; price: number; currency: string };
type ApiCart = { id: string; subtotal: string; item_count: number; items: { id: string; quantity: number; line_total: string; product: { id: string; name: string; brand?: string; image_url?: string; price: string; currency: string } }[] };
type CartLine = { id: string; product_id: string; quantity: number; line_total: number; product: Product };

function readGuestCart(): { product_id: string; quantity: number }[] {
  try { const parsed = JSON.parse(localStorage.getItem(GUEST_CART_KEY) || '[]'); return Array.isArray(parsed) ? parsed : []; } catch { return []; }
}
function writeGuestCart(items: { product_id: string; quantity: number }[]) { localStorage.setItem(GUEST_CART_KEY, JSON.stringify(items)); window.dispatchEvent(new Event('gy-cart-changed')); }
function money(v: number) { return `$${Number(v || 0).toFixed(2)}`; }

export default function CartPage() {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [message, setMessage] = useState('Loading cart...');
  const [isGuest, setIsGuest] = useState(false);
  const token = () => localStorage.getItem('gy_customer_token') || '';

  const subtotal = useMemo(() => lines.reduce((sum, item) => sum + item.line_total, 0), [lines]);
  const itemCount = useMemo(() => lines.reduce((sum, item) => sum + item.quantity, 0), [lines]);

  async function loadGuest() {
    setIsGuest(true);
    const guest = readGuestCart();
    if (!guest.length) { setLines([]); setMessage(''); return; }
    const res = await fetch(`${API}/api/v1/catalog/products?limit=250`, { cache: 'no-store' });
    const products: Product[] = res.ok ? await res.json() : [];
    const byId = new Map(products.map((p) => [p.id, p]));
    const next = guest.map((item) => {
      const product = byId.get(item.product_id);
      if (!product) return null;
      return { id: item.product_id, product_id: item.product_id, quantity: item.quantity, line_total: Number(product.price) * item.quantity, product };
    }).filter(Boolean) as CartLine[];
    setLines(next); setMessage('');
  }

  async function load() {
    const t = token();
    if (!t) { await loadGuest(); return; }
    setIsGuest(false);
    const res = await fetch(`${API}/api/v1/commerce/cart`, { headers: { Authorization: `Bearer ${t}` } });
    const json: ApiCart = await res.json();
    if (!res.ok) throw new Error((json as any).detail || 'Cart unavailable');
    setLines(json.items.map((item) => ({
      id: item.id,
      product_id: item.product.id,
      quantity: item.quantity,
      line_total: Number(item.line_total),
      product: { ...item.product, price: Number(item.product.price) },
    })));
    setMessage('');
  }

  async function updateItem(id: string, quantity: number) {
    if (isGuest) {
      const next = readGuestCart().map((item) => item.product_id === id ? { ...item, quantity } : item).filter((item) => item.quantity > 0);
      writeGuestCart(next);
      await loadGuest();
      return;
    }
    const res = await fetch(`${API}/api/v1/commerce/cart/items/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify({ quantity }) });
    const json = await res.json();
    if (!res.ok) { setMessage(json.detail || 'Update failed'); return; }
    setLines(json.items.map((item: any) => ({ id: item.id, product_id: item.product.id, quantity: item.quantity, line_total: Number(item.line_total), product: { ...item.product, price: Number(item.product.price) } })));
    window.dispatchEvent(new Event('gy-cart-changed'));
  }

  useEffect(() => { load().catch((e) => setMessage(String(e))); }, []);

  return <main className="commercePage"><a href="/products">← Continue shopping</a><h1>Your Cart</h1>{message && <div className="authNotice">{message}</div>}{isGuest && lines.length > 0 && <div className="authNotice">You are checking a guest cart. Sign in during checkout to save it to your account.</div>}<div className="cartList">{lines.length === 0 ? <p>Your cart is empty.</p> : lines.map((i) => <article className="cartItem" key={i.id}>{i.product.image_url && <img src={i.product.image_url} alt={i.product.name} />}<div><strong>{i.product.name}</strong><span>{i.product.brand}</span><span>{money(i.product.price)}</span></div><div className="qty"><button onClick={() => updateItem(i.id, Math.max(0, i.quantity - 1))}>−</button><b>{i.quantity}</b><button onClick={() => updateItem(i.id, i.quantity + 1)}>+</button></div><b>{money(i.line_total)}</b></article>)}</div><section className="summary"><p>Items: {itemCount}</p><h2>Subtotal {money(subtotal)}</h2><p>{subtotal >= 70 ? 'Free shipping unlocked.' : `${money(70 - subtotal)} away from free shipping.`}</p>{isGuest ? <a className="primaryLink" href="/login">Sign in to checkout</a> : <a className="primaryLink" href="/checkout">Checkout</a>}</section></main>;
}
