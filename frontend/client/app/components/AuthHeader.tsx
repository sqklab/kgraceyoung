'use client';

import { useEffect, useMemo, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type User = { email: string; full_name?: string; role?: string; locale?: string };

function UserIcon() {
  return (<svg width="38" height="38" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 12.2a4.2 4.2 0 1 0 0-8.4 4.2 4.2 0 0 0 0 8.4Z" fill="none" stroke="currentColor" strokeWidth="1.85"/><path d="M4.6 21a7.4 7.4 0 0 1 14.8 0" fill="none" stroke="currentColor" strokeWidth="1.85" strokeLinecap="round"/></svg>);
}
function BagIcon() {
  return (<svg width="38" height="38" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.2 8.3h11.6l.8 12.2H5.4l.8-12.2Z" fill="none" stroke="currentColor" strokeWidth="1.9"/><path d="M8.8 8.3V6.7a3.2 3.2 0 0 1 6.4 0v1.6" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"/></svg>);
}
function HeartIcon() {
  return (<svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.2S4.7 16 3.2 10.6C2.1 6.8 6.4 4.3 9.2 6.7L12 9.1l2.8-2.4c2.8-2.4 7.1.1 6 3.9C19.3 16 12 20.2 12 20.2Z" fill="currentColor"/></svg>);
}
function GlobeIcon() {
  return (<svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.9"/><path d="M3 12h18M12 3c2.3 2.4 3.5 5.4 3.5 9S14.3 18.6 12 21M12 3C9.7 5.4 8.5 8.4 8.5 12s1.2 6.6 3.5 9" fill="none" stroke="currentColor" strokeWidth="1.55" strokeLinecap="round"/></svg>);
}

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
    if (!token) { setReady(true); return; }
    fetch(`${API}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (res) => {
        const json = await res.json().catch(() => null);
        if (!res.ok || !json) throw new Error('Session expired');
        if (!cancelled) { setUser(json); localStorage.setItem('gy_customer_user', JSON.stringify(json)); }
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
    window.addEventListener('focus', syncAuth);
    return () => { cancelled = true; window.removeEventListener('storage', syncAuth); window.removeEventListener('gy-auth-changed', syncAuth as EventListener); window.removeEventListener('focus', syncAuth); };
  }, []);

  const displayName = useMemo(() => user?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'Grace', [user]);
  function logout() {
    localStorage.removeItem('gy_customer_token');
    localStorage.removeItem('gy_customer_user');
    setUser(null); setOpen(false); window.dispatchEvent(new Event('gy-auth-changed'));
  }

  if (!ready && !user) return <div className="sbHeaderActions"><span className="sbHeaderSkeleton" /><span className="sbHeaderSkeleton" /></div>;

  return (
    <div className="sbHeaderActions authMenuWrap">
      <a className="sbActionItem sbCartAction" href="/cart"><BagIcon /><span>Shopping Cart</span><b>0</b></a>
      <a className="sbActionItem" href="/wishlist"><HeartIcon /><span>My Wish Lists</span></a>
      {user ? (
        <button className="sbActionItem sbAccountAction" onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-label="My account"><UserIcon /><span>{displayName}</span></button>
      ) : (
        <a className="sbActionItem sbAccountAction" href="/login"><UserIcon /><span>Sign In or Create an account</span></a>
      )}
      <span className="sbIconOnly"><GlobeIcon /></span>
      {open && user && (
        <div className="accountDropdown sbAccountDropdown">
          <a href="/account">My Grace</a><a href="/orders">Track Orders</a><a href="/wishlist">My Wish List</a><button onClick={logout}>Logout</button>
        </div>
      )}
    </div>
  );
}
