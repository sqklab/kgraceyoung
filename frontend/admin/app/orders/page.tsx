'use client';

import { useEffect, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Order = { id: string; email: string; status: string; payment_status: string; fulfillment_status: string; grand_total: number; currency: string; shipping_country?: string; created_at?: string; items: { product_name: string; quantity: number; line_total: number }[] };

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [message, setMessage] = useState('Loading orders...');
  useEffect(() => {
    const t = localStorage.getItem('gy_admin_token') || '';
    if (!t) { window.location.href = '/login'; return; }
    fetch(`${API}/api/v1/admin/orders`, { headers: { Authorization: `Bearer ${t}` } })
      .then(async res => { const json = await res.json(); if (!res.ok) throw new Error(json.detail || 'Orders unavailable'); setOrders(json); setMessage(''); })
      .catch(e => setMessage(String(e)));
  }, []);
  return <main className="adminPage"><header className="adminHeader"><a href="/">← Dashboard</a><h1>Orders</h1><p>Phase 5 order creation monitor. Payment and shipping labels will be connected next.</p></header>{message && <div className="notice">{message}</div>}<section className="panel"><div className="orderTable">{orders.length === 0 ? <p>No orders yet.</p> : orders.map(o => <article className="orderRow" key={o.id}><div><strong>#{o.id.slice(0, 8)}</strong><span>{o.email}</span><small>{o.items.map(i => `${i.product_name} x${i.quantity}`).join(', ')}</small></div><div><b>${Number(o.grand_total).toFixed(2)}</b><span>{o.status}</span><small>{o.payment_status} · {o.fulfillment_status}</small></div></article>)}</div></section></main>;
}
