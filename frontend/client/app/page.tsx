import CommerceHeader from './components/CommerceHeader';
import ProductActions from './components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

const filterGroups = [
  { title: 'Category', items: ['Sheet Masks', 'Serum & Ampoule', 'Suncare', 'Toner Pads', 'Beauty Devices'] },
  { title: 'Skin Concern', items: ['Dark Spots', 'Acne Marks', 'Sensitive', 'Moisturising', 'Firming'] },
  { title: 'Key Ingredients', items: ['Centella Asiatica', 'Rice', 'Green Tea', 'Heartleaf', 'Ginseng'] },
  { title: 'Shopping Benefit', items: ['Hot Deal', 'Best', 'New', 'Free Shipping', 'Grace Rewards'] },
];

const heroSlides = [
  { image: '/hero/beauty-slide-1.svg', label: 'Seoul glow rituals', title: 'Clean glow routines, fresh from Seoul.', cta: 'Shop new beauty' },
  { image: '/hero/beauty-slide-2.svg', label: 'Sensitive & barrier', title: 'Cica comfort for calm skin days.', cta: 'Explore cica care' },
  { image: '/hero/beauty-slide-3.svg', label: 'Firming & devices', title: 'Premium device picks for home rituals.', cta: 'Shop devices' },
];

const quickMenus = ['Best', 'New', 'Only at Grace', 'Cica', 'SPF', 'Masks', 'Devices', 'Reels'];

async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${API}/api/v1/catalog/products?limit=24`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function formatMoney(value: number) {
  return `US$${Number(value || 0).toFixed(2)}`;
}

export default async function Home() {
  const products = await getProducts();
  return (
    <main className="kurlyShell">
      <CommerceHeader />

      <section className="topVisualSlider" aria-label="Grace Young beauty promotions">
        <div className="slideTrack">
          {heroSlides.map((slide, index) => (
            <article className="visualSlide" key={slide.title} aria-hidden={index !== 0}>
              <img src={slide.image} alt="" />
              <div className="slideOverlay">
                <span>{slide.label}</span>
                <h1>{slide.title}</h1>
                <a href="#best">{slide.cta}</a>
              </div>
            </article>
          ))}
        </div>
        <button className="slideArrow prev" aria-label="Previous slide">‹</button>
        <button className="slideArrow next" aria-label="Next slide">›</button>
        <div className="slideDots" aria-hidden="true"><span /><span /><span /></div>
      </section>

      <section className="quickMenuStrip" aria-label="Quick shopping menus">
        {quickMenus.map((item, idx) => <a key={item} className={idx === 2 ? 'active' : ''} href="#best">{item}</a>)}
      </section>

      <section className="promoBand">
        <span>✈ Free shipping over US$49</span>
        <span>▣ Reels commerce ready</span>
        <span>♡ Grace Rewards points</span>
      </section>

      <section className="catalogLayoutKurly" id="best">
        <aside className="filterPanelKurly">
          <div className="filterTitle"><b>Refine</b><a href="#best">Clear all</a></div>
          <div className="selectedChip">Centella Asiatica Extract <button>×</button></div>
          {filterGroups.map((group) => (
            <section className="filterGroupKurly" key={group.title}>
              <h3>{group.title}<span>−</span></h3>
              {group.items.map((item, index) => (
                <label key={item}>
                  <input type="checkbox" defaultChecked={group.title === 'Key Ingredients' && index === 0} />
                  <span>{item}</span>
                  <small>({index * 37 + 10})</small>
                </label>
              ))}
            </section>
          ))}
        </aside>

        <section className="catalogMainKurly">
          <div className="listToolbarKurly">
            <div><strong>{products.length || 0}</strong> items <i /> view <button className="selected">24</button><button>36</button><button>48</button></div>
            <select defaultValue="popular"><option value="popular">Most Popular</option><option value="new">New Arrivals</option><option value="price">Price Low to High</option></select>
          </div>

          <div className="productGridKurly">
            {products.length === 0 ? <article className="emptyCatalog">No products yet. Run <b>seed_phase2_catalog.py</b>.</article> : products.map((p, index) => (
              <article className="productCardKurly" key={p.id}>
                <div className="productThumbKurly">
                  <div className="badgeStack">
                    {index % 4 === 0 && <span className="hotBadge">HOT DEAL</span>}
                    {index % 3 === 0 && <span className="onlyBadge">GRACE ONLY</span>}
                    {index % 3 !== 0 && <span className="bestBadge">BEST</span>}
                  </div>
                  {p.image_url ? <img src={p.image_url} alt={p.name} /> : <div className="empty">No image</div>}
                  <button className="cartFloat" aria-label="Add to cart">🛍</button>
                </div>
                <small>{p.brand}</small>
                <strong>{p.name}</strong>
                <p>{p.description || 'Curated Korean beauty routine pick for daily glow.'}</p>
                <div className="ratingLine">★ {(4.5 + (index % 5) / 10).toFixed(1)}</div>
                <div className="priceLineKurly"><span>{formatMoney(p.price)}</span>{index % 4 === 0 && <del>{formatMoney(p.price * 1.35)}</del>}</div>
                <ProductActions productId={p.id} />
              </article>
            ))}
          </div>
        </section>
      </section>

      <section className="reelCommerceKurly" id="reels">
        <div className="sectionHeading"><span>Shop the Reel</span><h2>Watch routines and shop products in one flow.</h2></div>
        <div className="reelRailKurly">{['Cica + SPF', 'Glass skin toner', 'LED mask demo', 'Ginseng firming'].map((r) => <article key={r}><div>▶</div><strong>{r}</strong><button>Add routine</button></article>)}</div>
      </section>
    </main>
  );
}
