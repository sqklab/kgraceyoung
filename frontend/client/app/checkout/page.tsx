'use client';

import { FormEvent, useEffect, useState } from 'react';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Address = { id: string; label: string; full_name: string; line1: string; city: string; state?: string; postal_code: string; country: string; is_default: boolean };

type Order = { id: string; grand_total: string; status: string; payment_status: string };

export default function CheckoutPage() {
  const [addresses, setAddresses] = useState<Address[]>([]);
  const [selected, setSelected] = useState('');
  const [order, setOrder] = useState<Order | null>(null);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ label: 'Home', full_name: 'Grace Young Customer', phone: '', line1: '123 Beauty Ave', line2: '', city: 'Los Angeles', state: 'CA', postal_code: '90001', country: 'US', is_default: true });
  const token = () => localStorage.getItem('gy_customer_token') || '';
  async function load() { const t = token(); if (!t) { window.location.href = '/login'; return; } const res = await fetch(`${API}/api/v1/commerce/addresses`, { headers: { Authorization: `Bearer ${t}` } }); const json = await res.json(); if (res.ok) { setAddresses(json); setSelected(json.find((a: Address) => a.is_default)?.id || json[0]?.id || ''); } }
  useEffect(() => { load(); }, []);
  async function saveAddress(e: FormEvent) { e.preventDefault(); const res = await fetch(`${API}/api/v1/commerce/addresses`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify(form) }); const json = await res.json(); if (!res.ok) { setMessage(json.detail || 'Address failed'); return; } setAddresses([json, ...addresses]); setSelected(json.id); setMessage('Address saved'); }
  async function checkout() { const body = selected ? { shipping_address_id: selected } : { address: form }; const res = await fetch(`${API}/api/v1/commerce/checkout`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` }, body: JSON.stringify(body) }); const json = await res.json(); if (!res.ok) { setMessage(json.detail || 'Checkout failed'); return; } setOrder(json); setMessage('Order created. Payment integration will be connected in the next phase.'); }
  return <main className="commercePage"><a href="/cart">← Cart</a><h1>Checkout</h1>{message && <div className="authNotice">{message}</div>}{order ? <section className="accountCard"><span className="pill">Order Created</span><h2>Order #{order.id.slice(0, 8)}</h2><p>Status: {order.status} / {order.payment_status}</p><h2>Total ${Number(order.grand_total).toFixed(2)}</h2><a className="primaryLink" href="/orders">View orders</a></section> : <><section className="panelLike"><h2>Shipping address</h2>{addresses.length > 0 && <label>Saved address<select value={selected} onChange={(e) => setSelected(e.target.value)}>{addresses.map((a) => <option key={a.id} value={a.id}>{a.label} · {a.line1}, {a.city}</option>)}</select></label>}<form className="checkoutForm" onSubmit={saveAddress}>{Object.entries(form).filter(([k]) => k !== 'is_default').map(([k, v]) => <label key={k}>{k}<input value={String(v)} onChange={(e) => setForm((prev) => ({ ...prev, [k]: e.target.value } as typeof prev))} /></label>)}<button>Save address</button></form></section><button className="checkoutButton" onClick={checkout}>Create Order</button></>}</main>;
}
