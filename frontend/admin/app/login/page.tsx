'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AdminLoginPage() {
  const [email, setEmail] = useState('admin@graceyoung.local');
  const [password, setPassword] = useState('Admin123!');
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
  }

  return (
    <main className="loginPage">
      <form className="loginCard" onSubmit={submit}>
        <span className="badge">Admin Login</span>
        <h1>Grace Young</h1>
        <p>Use the seeded admin account after running the Phase 3 seed script.</p>
        {message && <div className="notice">{message}</div>}
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <button>Sign in to Admin</button>
        <small>Seeded account: admin@graceyoung.local / Admin123!</small>
      </form>
    </main>
  );
}
