'use client';

import { useEffect, useState } from 'react';

const cards = [
  ['Products', 'Create, edit, and review product catalog records', '/products'],
  ['Brands', '5 sample brands per category are seeded in Phase 2', '/products'],
  ['Categories', 'Skincare, Suncare, Face Masks, Makeup, Devices', '/products'],
  ['Uploads', 'Product images are stored in MinIO product bucket', '/products'],
  ['Reels', 'Next phase: upload videos and tag products', '#'],
  ['Orders', 'Review pending customer orders created from checkout', '/orders'],
];

export default function AdminHome() {
  const [user, setUser] = useState<{ full_name?: string; email: string; role: string } | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('gy_admin_token');
    const saved = localStorage.getItem('gy_admin_user');
    if (!token) {
      window.location.href = '/login';
      return;
    }
    if (saved) setUser(JSON.parse(saved));
  }, []);

  function logout() {
    localStorage.removeItem('gy_admin_token');
    localStorage.removeItem('gy_admin_user');
    window.location.href = '/login';
  }

  return (
    <main className="shell">
      <aside>
        <h1>Grace Young</h1>
        <p>Admin Console</p>
        <span className="badge">Phase 5 Commerce</span>
        <div className="adminTopActions">
          <a className="primary" href="/products">Products</a>
          <a href="/orders">Orders</a>
          <button onClick={logout}>Logout</button>
        </div>
      </aside>
      <section>
        <h2>Operations Dashboard</h2>
        <p className="muted">Signed in as {user?.full_name || user?.email || 'admin'} · role: {user?.role || 'admin'}</p>
        <p className="muted">Catalog and order APIs are protected by JWT bearer tokens and admin-role authorization.</p>
        <div className="grid">
          {cards.map(([a,b,href]) => (
            <a className="cardLink" href={href} key={a}><strong>{a}</strong><span>{b}</span></a>
          ))}
        </div>
      </section>
    </main>
  );
}
