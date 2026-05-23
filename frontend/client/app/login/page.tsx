'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function CustomerLoginPage() {
  const [email, setEmail] = useState('customer@graceyoung.local');
  const [password, setPassword] = useState('Customer123!');
  const [message, setMessage] = useState('');

  async function submit(e: FormEvent) {
    e.preventDefault();
    setMessage('');
    const res = await fetch(`${API}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const json = await res.json();
    if (!res.ok) { setMessage(json.detail || 'Login failed'); return; }
    localStorage.setItem('gy_customer_token', json.access_token);
    localStorage.setItem('gy_customer_user', JSON.stringify(json.user));
    window.location.href = '/account';
  }

  return (
    <main className="authPage">
      <form className="authCard" onSubmit={submit}>
        <span className="pill">Customer Login</span>
        <h1>Welcome back</h1>
        <p>Sign in to save routines, build wishlists, and earn Grace Rewards points.</p>
        {message && <div className="authNotice">{message}</div>}
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button>Sign in</button>
        <a href="/register">Create a new account</a>
      </form>
    </main>
  );
}
