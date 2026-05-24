import CommerceHeader from './components/CommerceHeader';
import ProductActions from './components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

const filterGroups = [
  { title: 'Face Masks Category', items: ['Sheet Masks', 'Facial Masks', 'Nose Pack', 'Patches', 'Pads'] },
  { title: 'Skin Concern', items: ['Acne', 'Blackheads', 'Brightening', 'Sensitive', 'Moisturising', 'Well-aging'] },
  { title: 'Key Ingredients', items: ['Centella Asiatica Extract', 'Rice', 'Green Tea', 'Heartleaf', 'Ginseng'] },
];
const concernChips = ['Cica Care', 'Dark Spot', 'SPF', 'Barrier', 'Firming'];
const heroTiles = ['Best Sellers', 'K-Beauty Devices', 'Daily SPF', 'Reels Picks'];

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
    <main className="commerceShell">
      <CommerceHeader />

      <section className="commerceHero">
        <div className="heroCopy">
          <p className="eyebrow">K-Beauty Video Commerce</p>
          <h1>Discover Korean beauty through trusted curation.</h1>
          <p>Shop Grace Young’s curated skincare, SPF, face masks, and devices with reels-based product discovery for the Americas.</p>
          <div className="heroCtas"><a className="primaryLink" href="#best">Shop Best</a><a className="secondaryLink" href="#reels">Watch Reels</a></div>
        </div>
        <div className="heroPromoGrid">
          {heroTiles.map((item, idx) => <article key={item} className={`promoTile promo${idx}`}><span>{item}</span><b>{idx === 0 ? 'Up to 35%' : 'Curated'}</b></article>)}
        </div>
      </section>

      <section className="quickChips" aria-label="Quick filters">
        <b>Refine</b>
        {concernChips.map((chip) => <a key={chip} href="#best">{chip}<span>×</span></a>)}
      </section>

      <section className="catalogLayout" id="best">
        <aside className="filterPanel">
          {filterGroups.map((group) => (
            <section className="filterGroup" key={group.title}>
              <h3>{group.title}<span>−</span></h3>
              {group.items.map((item, index) => <label key={item}><input type="checkbox" /> {item} <small>({index * 17 + 10})</small></label>)}
            </section>
          ))}
        </aside>

        <section className="catalogMain">
          <div className="listToolbar">
            <div><b>{products.length || 0}</b> items <span className="divider" /> view <button>24</button><button>36</button><button>48</button></div>
            <select defaultValue="popular"><option value="popular">Most Popular</option><option value="new">New Arrivals</option><option value="price">Price Low to High</option></select>
          </div>

          <div className="productGridDense">
            {products.length === 0 ? <article className="emptyCatalog">No products yet. Run <b>seed_phase2_catalog.py</b>.</article> : products.map((p, index) => (
              <article className="productCardOY" key={p.id}>
                <div className="badgeRow"><span className={index % 3 === 0 ? 'hotBadge' : 'bestBadge'}>{index % 3 === 0 ? 'HOT DEAL' : 'BEST'}</span><button className="bagIcon" aria-label="Quick bag">♧</button></div>
                <div className="productImageWrap">{p.image_url ? <img src={p.image_url} alt={p.name} /> : <div className="empty">No image</div>}</div>
                <small>{p.brand}</small>
                <strong>{p.name}</strong>
                <div className="rating">★ {(4.5 + (index % 5) / 10).toFixed(1)}</div>
                <div className="priceLine"><span>{formatMoney(p.price)}</span>{index % 4 === 0 && <del>{formatMoney(p.price * 1.35)}</del>}</div>
                <ProductActions productId={p.id} />
              </article>
            ))}
          </div>
        </section>
      </section>

      <section className="reelCommerce" id="reels">
        <div><p className="eyebrow">Shop the Reel</p><h2>Watch routines, then add the products in one flow.</h2></div>
        <div className="reelRail">{['Cica + SPF', 'Glass skin toner', 'LED mask demo', 'Ginseng firming'].map((r) => <article key={r}><div className="play">▶</div><strong>{r}</strong><button>Add routine</button></article>)}</div>
      </section>
    </main>
  );
}
