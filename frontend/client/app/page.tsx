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
  {
    image: 'https://source.unsplash.com/1800x560/?korean,skincare,cosmetics&sig=101',
    label: 'DAILY K-BEAUTY',
    title: 'Everyday glow care, curated for sensitive skin.',
    cta: 'Shop now'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?beauty,serum,skincare&sig=102',
    label: 'CICA ROUTINE',
    title: 'Calming care for barrier-first beauty rituals.',
    cta: 'Explore cica'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?sunscreen,beauty,skincare&sig=103',
    label: 'SUN CARE',
    title: 'Lightweight SPF picks for every day.',
    cta: 'Shop SPF'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?lipstick,cosmetics,pink&sig=104',
    label: 'LIP CARE',
    title: 'Soft lip color and glossy care in one routine.',
    cta: 'Shop lip care'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?makeup,cosmetics,flatlay&sig=105',
    label: 'MAKEUP',
    title: 'Fresh color stories for clean daily looks.',
    cta: 'Shop makeup'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?face,mask,skincare&sig=106',
    label: 'MASK BAR',
    title: 'Sheet masks and pads for quick glow days.',
    cta: 'Shop masks'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?haircare,beauty,bottle&sig=107',
    label: 'HAIR CARE',
    title: 'Scalp and hair rituals for healthy shine.',
    cta: 'Shop hair'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?bodycare,cosmetics,lotion&sig=108',
    label: 'BODY CARE',
    title: 'Body glow essentials for soft, smooth skin.',
    cta: 'Shop body'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?beauty,device,led&sig=109',
    label: 'DEVICES',
    title: 'Home beauty devices for routine upgrades.',
    cta: 'Shop devices'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?perfume,beauty,clean&sig=110',
    label: 'FRAGRANCE',
    title: 'Clean scents and soft mood essentials.',
    cta: 'Shop fragrance'
  },
  {
    image: 'https://source.unsplash.com/1800x560/?organic,cosmetics,spa&sig=111',
    label: 'CLEAN BEAUTY',
    title: 'Ingredient-led beauty with gentle daily care.',
    cta: 'Shop clean picks'
  },
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
        <div className="slideDots" aria-hidden="true">{heroSlides.map((_, i) => <span key={i} className={i === 0 ? 'active' : ''} />)}</div>
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
