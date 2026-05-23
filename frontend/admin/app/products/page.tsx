'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

type Category = { id: string; slug: string; name: string };
type Brand = { id: string; slug: string; name: string };
type Product = {
  id: string;
  slug: string;
  name: string;
  price: string;
  currency: string;
  status: string;
  brand?: Brand;
  categories?: Category[];
  images?: { url: string }[];
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ProductsPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [message, setMessage] = useState('');
  const [imageUrl, setImageUrl] = useState('');
  const [token, setToken] = useState('');
  const [form, setForm] = useState({
    name: 'Cica Barrier Serum Admin Sample',
    slug: 'cica-barrier-serum-admin-sample',
    short_description: 'Admin-created sample product with MinIO image upload support.',
    price: '24.00',
    brand_id: '',
    category_id: '',
  });

  async function load() {
    const savedToken = localStorage.getItem('gy_admin_token') || '';
    if (!savedToken) { window.location.href = '/login'; return; }
    setToken(savedToken);
    const authHeaders = { Authorization: `Bearer ${savedToken}` };
    const [catRes, brandRes, productRes] = await Promise.all([
      fetch(`${API}/api/v1/admin/catalog/categories`, { headers: authHeaders }),
      fetch(`${API}/api/v1/admin/catalog/brands`, { headers: authHeaders }),
      fetch(`${API}/api/v1/admin/catalog/products?limit=40`, { headers: authHeaders }),
    ]);
    const catData = await catRes.json();
    const brandData = await brandRes.json();
    setCategories(catData);
    setBrands(brandData);
    setProducts(await productRes.json());
    setForm((prev) => ({
      ...prev,
      brand_id: prev.brand_id || brandData?.[0]?.id || '',
      category_id: prev.category_id || catData?.[0]?.id || '',
    }));
  }

  useEffect(() => { load().catch((e) => setMessage(String(e))); }, []);

  const canCreate = useMemo(() => form.name && form.slug && form.brand_id && form.category_id, [form]);

  async function uploadImage(file: File) {
    const data = new FormData();
    data.append('file', file);
    const authToken = token || localStorage.getItem('gy_admin_token') || '';
    const res = await fetch(`${API}/api/v1/admin/catalog/images/upload`, { method: 'POST', headers: { Authorization: `Bearer ${authToken}` }, body: data });
    if (!res.ok) throw new Error(await res.text());
    const json = await res.json();
    setImageUrl(json.url);
    setMessage('Image uploaded to MinIO.');
  }

  async function createProduct(e: FormEvent) {
    e.preventDefault();
    const res = await fetch(`${API}/api/v1/admin/catalog/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token || localStorage.getItem('gy_admin_token') || ''}` },
      body: JSON.stringify({
        slug: form.slug,
        name: form.name,
        short_description: form.short_description,
        price: form.price,
        currency: 'USD',
        status: 'published',
        brand_id: form.brand_id,
        category_ids: [form.category_id],
        image_urls: imageUrl ? [imageUrl] : [],
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    setMessage('Product created.');
    await load();
  }

  return (
    <main className="adminPage">
      <header className="adminHeader">
        <a href="/">← Dashboard</a>
        <h1>Products</h1>
        <p>Phase 2 CRUD: category, brand, product creation, and MinIO image upload.</p>
      </header>

      {message && <div className="notice">{message}</div>}

      <section className="panel">
        <h2>Create Product</h2>
        <form className="form" onSubmit={(e) => createProduct(e).catch((err) => setMessage(String(err)))}>
          <label>Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
          <label>Slug<input value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} /></label>
          <label>Description<textarea value={form.short_description} onChange={(e) => setForm({ ...form, short_description: e.target.value })} /></label>
          <label>Price<input value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /></label>
          <label>Brand<select value={form.brand_id} onChange={(e) => setForm({ ...form, brand_id: e.target.value })}>{brands.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></label>
          <label>Category<select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
          <label>Image Upload<input type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && uploadImage(e.target.files[0]).catch((err) => setMessage(String(err)))} /></label>
          {imageUrl && <img className="preview" src={imageUrl} alt="Uploaded product" />}
          <button disabled={!canCreate}>Create Product</button>
        </form>
      </section>

      <section className="panel">
        <h2>Latest Products</h2>
        <div className="productGrid">
          {products.map((p) => (
            <article className="productCard" key={p.id}>
              {p.images?.[0]?.url ? <img src={p.images[0].url} alt={p.name} /> : <div className="emptyImg">No image</div>}
              <strong>{p.name}</strong>
              <span>{p.brand?.name || 'No brand'} · ${p.price}</span>
              <small>{p.categories?.map((c) => c.name).join(', ')}</small>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
