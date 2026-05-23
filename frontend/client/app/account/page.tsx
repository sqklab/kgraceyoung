'use client';

import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type User = { email: string; full_name?: string; role: string; locale: string };

export default function AccountPage() {
  const [user, setUser] = useState<User | null>(null);
  const [message, setMessage] = useState('Loading account...');

  useEffect(() => {
    const token = localStorage.getItem('gy_customer_token');
    if (!token) { window.location.href = '/login'; return; }
    fetch(`${API}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (res) => {
        const json = await res.json();
        if (!res.ok) throw new Error(json.detail || 'Account unavailable');
        setUser(json);
        setMessage('');
      })
      .catch((err) => {
        setMessage(String(err));
        localStorage.removeItem('gy_customer_token');
      });
  }, []);

  function logout() {
    localStorage.removeItem('gy_customer_token');
    localStorage.removeItem('gy_customer_user');
    window.location.href = '/';
  }

  return (
    <main className="accountPage">
      <a href="/">← Grace Young</a>
      <section className="accountCard">
        <span className="pill">My Grace</span>
        <h1>{user?.full_name || 'My Account'}</h1>
        {message ? <p>{message}</p> : <>
          <p><b>Email:</b> {user?.email}</p>
          <p><b>Role:</b> {user?.role}</p>
          <p><b>Locale:</b> {user?.locale}</p>
          <div className="accountGrid">
            <article><strong>Grace Rewards</strong><span>Starter tier</span></article>
            <article><strong>Wishlist</strong><span><a href="/wishlist">Saved products</a></span></article>
            <article><strong>Orders</strong><span><a href="/orders">Order history</a></span></article>
            <article><strong>Cart</strong><span><a href="/cart">Review cart</a></span></article>
          </div>
          <button onClick={logout}>Logout</button>
        </>}
      </section>
    </main>
  );
}
