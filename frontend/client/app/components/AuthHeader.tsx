'use client';

import { useEffect, useMemo, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type User = { email: string; full_name?: string; role?: string; locale?: string };

export default function AuthHeader() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const token = localStorage.getItem('gy_customer_token');
    const cached = localStorage.getItem('gy_customer_user');

    if (cached) {
      try { setUser(JSON.parse(cached)); } catch { localStorage.removeItem('gy_customer_user'); }
    }

    if (!token) {
      setReady(true);
      return;
    }

    fetch(`${API}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (res) => {
        const json = await res.json().catch(() => null);
        if (!res.ok || !json) throw new Error('Session expired');
        if (!cancelled) {
          setUser(json);
          localStorage.setItem('gy_customer_user', JSON.stringify(json));
        }
      })
      .catch(() => {
        localStorage.removeItem('gy_customer_token');
        localStorage.removeItem('gy_customer_user');
        if (!cancelled) setUser(null);
      })
      .finally(() => { if (!cancelled) setReady(true); });

    const syncAuth = () => {
      const next = localStorage.getItem('gy_customer_user');
      if (!next) { setUser(null); return; }
      try { setUser(JSON.parse(next)); } catch { setUser(null); }
    };
    window.addEventListener('storage', syncAuth);
    window.addEventListener('gy-auth-changed', syncAuth as EventListener);
    return () => {
      cancelled = true;
      window.removeEventListener('storage', syncAuth);
      window.removeEventListener('gy-auth-changed', syncAuth as EventListener);
    };
  }, []);

  const displayName = useMemo(() => user?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'My Grace', [user]);

  function logout() {
    localStorage.removeItem('gy_customer_token');
    localStorage.removeItem('gy_customer_user');
    setUser(null);
    setOpen(false);
    window.dispatchEvent(new Event('gy-auth-changed'));
  }

  if (!ready && !user) {
    return <div className="iconActions"><span className="iconSkeleton" /><span className="iconSkeleton" /><span className="iconSkeleton" /></div>;
  }

  if (user) {
    return (
      <div className="iconActions authMenuWrap">
        <button className="iconButton accountButton" onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-label="My account">
          <span className="accountGlyph">♡</span>
          <span>{displayName}</span>
        </button>
        <a className="iconButton" href="/wishlist" aria-label="Wishlist">♡</a>
        <a className="iconButton" href="/cart" aria-label="Cart">Bag</a>
        {open && (
          <div className="accountDropdown">
            <a href="/account">My Grace</a>
            <a href="/orders">Track Orders</a>
            <a href="/wishlist">My Wishlist</a>
            <button onClick={logout}>Logout</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="iconActions authMenuWrap">
      <a className="iconButton accountButton" href="/login"><span className="accountGlyph">♡</span><span>Sign In</span></a>
      <a className="iconButton" href="/cart" aria-label="Cart">Bag</a>
      <a className="joinLink" href="/register">Join</a>
    </div>
  );
}
