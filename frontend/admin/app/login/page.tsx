'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function friendlyError(error: unknown) {
  const msg = error instanceof Error ? error.message : String(error);
  if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
    return `API connection failed. Check DNS/proxy for ${API}.`;
  }
  return msg;
}

export default function AdminLoginPage() {
  const [email, setEmail] = useState('admin@graceyoung.local');
  const [password, setPassword] = useState('Admin123!');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setMessage('');
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) {
        setMessage(json.detail || 'Login failed');
        return;
      }
      if (!['admin', 'super_admin'].includes(json.user.role)) {
        setMessage('This account is not an admin account.');
        return;
      }
      localStorage.setItem('gy_admin_token', json.access_token);
      localStorage.setItem('gy_admin_user', JSON.stringify(json.user));
      window.location.href = '/';
    } catch (err) {
      setMessage(friendlyError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="loginPage premiumLoginPage">
      <form className="loginCard premiumLoginCard" onSubmit={submit}>
        <span className="badge">Admin Console</span>
        <h1>Grace Young</h1>
        <p>Manage catalog, images, orders, and curation with a protected admin session.</p>
        {message && <div className="notice">{message}</div>}
        <label>Email<input autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input autoComplete="current-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button disabled={loading}>{loading ? 'Signing in…' : 'Sign in to Admin'}</button>
        <small>Seeded account: admin@graceyoung.local / Admin123!</small>
      </form>
    </main>
  );
}
