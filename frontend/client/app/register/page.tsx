'use client';

import { FormEvent, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('Grace Young Customer');
  const [email, setEmail] = useState('new.customer@kgraceyoung.com');
  const [password, setPassword] = useState('Customer123!');
  const [locale, setLocale] = useState('en');
  const [message, setMessage] = useState('');

  async function submit(e: FormEvent) {
    e.preventDefault();
    setMessage('');
    const res = await fetch(`${API}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ full_name: fullName, email, password, locale }),
    });
    const json = await res.json();
    if (!res.ok) { setMessage(json.detail || 'Registration failed'); return; }
    localStorage.setItem('gy_customer_token', json.access_token);
    localStorage.setItem('gy_customer_user', JSON.stringify(json.user));
    window.location.href = '/account';
  }

  return (
    <main className="authPage">
      <form className="authCard" onSubmit={submit}>
        <span className="pill">Grace Rewards</span>
        <h1>Create account</h1>
        <p>Customer accounts are created as role <b>customer</b>. Admin access is separate.</p>
        {message && <div className="authNotice">{message}</div>}
        <label>Full name<input value={fullName} onChange={(e) => setFullName(e.target.value)} /></label>
        <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
        <label>Language<select value={locale} onChange={(e) => setLocale(e.target.value)}><option value="en">English</option><option value="fr">Français</option><option value="es">Español</option><option value="ko">한국어</option></select></label>
        <button>Create account</button>
        <a href="/login">Already have an account?</a>
      </form>
    </main>
  );
}
