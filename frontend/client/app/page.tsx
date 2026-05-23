import ProductActions from './components/ProductActions';
const concerns = ['Dark Spots & Melasma', 'Acne Marks', 'Daily SPF', 'Sensitive Barrier', 'Firming & Devices'];
const reels = ['Cica routine for acne marks', 'SPF glow test', 'LED mask demo', 'Ginseng anti-aging ritual'];
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${API}/api/v1/catalog/products?limit=12`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function Home() {
  const products = await getProducts();
  return (
    <main>
      <section className="topbar">Free shipping over $49 · English / Français / Español / 한국어</section>
      <header className="header">
        <div className="logo">Grace Young</div>
        <nav>
          <a>Skincare</a><a>Suncare</a><a>Devices</a><a>Brands</a><a>Reels</a><a href="/wishlist">Wishlist</a>
        </nav>
        <div className="headerActions"><a href="/login">Sign in</a><a href="/register">Join</a><a className="cart" href="/cart">Cart</a></div>
      </header>
      <section className="hero">
        <div>
          <p className="eyebrow">K-Beauty Video Commerce</p>
          <h1>Discover Korean beauty through reels, rituals, and trusted curation.</h1>
          <p className="lead">Olive Young-style curation, TikTok-style discovery, and Sephora-style confidence for the Americas.</p>
          <div className="actions"><button>Shop Best Sellers</button><button className="secondary">Watch Reels</button></div>
        </div>
        <div className="phone">
          <div className="reelCard">Shop the Reel<br/><span>Cica + SPF routine</span></div>
        </div>
      </section>
      <section className="section">
        <h2>Curated by skin concern</h2>
        <div className="grid">{concerns.map((c) => <article className="tile" key={c}>{c}<span>Explore routine →</span></article>)}</div>
      </section>
      <section className="section productsSection">
        <h2>Grace Young sample catalog</h2>
        <p className="sub">Seed Phase 2 to load 250 generated products with MinIO-hosted images.</p>
        <div className="products">
          {products.length === 0 ? <article className="tile">No products yet<span>Run backend seed_phase2_catalog.py</span></article> : products.map((p) => (
            <article className="product" key={p.id}>
              {p.image_url ? <img src={p.image_url} alt={p.name} /> : <div className="empty">No image</div>}
              <small>{p.brand}</small>
              <strong>{p.name}</strong>
              <span>${p.price.toFixed(2)}</span>
              <ProductActions productId={p.id} />
            </article>
          ))}
        </div>
      </section>
      <section className="section warm">
        <h2>Watch & shop reels</h2>
        <div className="reels">{reels.map((r) => <article className="vertical" key={r}><div className="play">▶</div><strong>{r}</strong><button>Add routine</button></article>)}</div>
      </section>
    </main>
  );
}
