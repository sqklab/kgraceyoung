'use client';

import { useEffect, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Order = { id: string; status: string; payment_status: string; grand_total: string; currency: string; items: { product_name: string; quantity: number }[] };
export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [message, setMessage] = useState('Loading orders...');
  useEffect(() => { const t = localStorage.getItem('gy_customer_token') || ''; if (!t) { window.location.href = '/login'; return; } fetch(`${API}/api/v1/commerce/orders`, { headers: { Authorization: `Bearer ${t}` } }).then(async res => { const json = await res.json(); if (!res.ok) throw new Error(json.detail || 'Orders unavailable'); setOrders(json); setMessage(''); }).catch(e => setMessage(String(e))); }, []);
  return <main className="commercePage"><a href="/account">← Account</a><h1>Orders</h1>{message && <div className="authNotice">{message}</div>}<div className="cartList">{orders.map((o) => <article className="cartItem" key={o.id}><div><strong>#{o.id.slice(0, 8)}</strong><span>{o.status} · {o.payment_status}</span><small>{o.items.map(i => `${i.product_name} x${i.quantity}`).join(', ')}</small></div><b>${Number(o.grand_total).toFixed(2)}</b></article>)}</div></main>;
}
