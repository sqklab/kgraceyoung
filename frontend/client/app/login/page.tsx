'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function friendlyError(error: unknown) {
  const msg = error instanceof Error ? error.message : String(error);
  if (msg.includes('Failed to fetch') || msg.includes('NetworkError')) {
    return `API connection failed. Check DNS/proxy for ${API}. If you use api.kgraceyoung.com, add an A record and Nginx Proxy Host for the API.`;
  }
  return msg;
}

export default function CustomerLoginPage() {
  const [email, setEmail] = useState('customer@graceyoung.local');
  const [password, setPassword] = useState('Customer123!');
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
      if (!res.ok) { setMessage(json.detail || 'Login failed. Check seed account and password.'); return; }
      localStorage.setItem('gy_customer_token', json.access_token);
      localStorage.setItem('gy_customer_user', JSON.stringify(json.user));
      window.location.href = '/account';
    } catch (err) {
      setMessage(friendlyError(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="authPage luxuryAuthPage">
      <section className="authShell">
        <aside className="authVisual">
          <a className="authBack" href="/">← Back to Grace Young</a>
          <div>
            <p className="eyebrow">Grace Rewards</p>
            <h2>Curated K-beauty rituals, saved for your next glow.</h2>
            <p>Sign in to save routines, build wishlists, and earn member-only rewards across skincare, SPF, and devices.</p>
          </div>
          <div className="authStats">
            <span>250 sample products</span>
            <span>Reels commerce ready</span>
          </div>
        </aside>
        <form className="authCard refinedAuthCard" onSubmit={submit}>
          <span className="pill">Customer Login</span>
          <h1>Welcome back</h1>
          <p className="muted">Use the seeded account after running the catalog seed script.</p>
          {message && <div className="authNotice">{message}</div>}
          <label>Email<input autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label>Password<input autoComplete="current-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
          <button className="primaryButton" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
          <div className="authLinks"><a href="/register">Create a new account</a><a href="/">Continue shopping</a></div>
        </form>
      </section>
    </main>
  );
}
