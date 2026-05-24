import CommerceHeader from './components/CommerceHeader';
import ProductActions from './components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

const heroSlides = [
  { image: '/hero/grace-hero-01.svg', title: 'Rose Glass Tint', subtitle: 'soft color layer', cta: 'SHOP NOW' },
  { image: '/hero/grace-hero-02.svg', title: 'Cica Calm Routine', subtitle: 'barrier-friendly skincare', cta: 'SHOP SKINCARE' },
  { image: '/hero/grace-hero-03.svg', title: 'Daily Sun Glow', subtitle: 'weightless SPF comfort', cta: 'SHOP SUN CARE' },
  { image: '/hero/grace-hero-04.svg', title: 'Violet Repair Serum', subtitle: 'plump and smooth', cta: 'DISCOVER' },
  { image: '/hero/grace-hero-05.svg', title: 'Hydra Dew Cream', subtitle: 'deep moisture finish', cta: 'SHOP CREAM' },
  { image: '/hero/grace-hero-06.svg', title: 'Lip Care Ritual', subtitle: 'glossy soft lips', cta: 'SHOP LIP CARE' },
  { image: '/hero/grace-hero-07.svg', title: 'Rice Bright Cleanse', subtitle: 'fresh clean glow', cta: 'SHOP CLEANSERS' },
  { image: '/hero/grace-hero-08.svg', title: 'Vegan Beauty Edit', subtitle: 'clean daily essentials', cta: 'SHOP VEGAN' },
];

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
  return `$${Number(value || 0).toFixed(2)}`;
}

export default async function Home() {
  const products = await getProducts();
  return (
    <main className="sbShell">
      <CommerceHeader />

      <section className="sbHero" aria-label="kgraceyoung promotional slides">
        <div className="sbHeroTrack">
          {heroSlides.map((slide, index) => (
            <article className="sbHeroSlide" key={slide.title} aria-hidden={index !== 0}>
              <img src={slide.image} alt="" />
              <div className="sbHeroCopy">
                <h1>{slide.title}</h1>
                <div />
                <p>{slide.subtitle}</p>
                <a href="#products">{slide.cta}</a>
              </div>
            </article>
          ))}
        </div>
        <button className="sbHeroArrow sbPrev" aria-label="Previous slide">‹</button>
        <button className="sbHeroArrow sbNext" aria-label="Next slide">›</button>
        <div className="sbHeroDots" aria-hidden="true">{heroSlides.slice(0, 4).map((_, i) => <span key={i} className={i === 0 ? 'active' : ''} />)}</div>
      </section>

      <section className="sbProductSection" id="products">
        <div className="sbSectionTitle">
          <h2>VEGAN LIP MASK 🌿</h2>
          <p>Cracked Lip Repair</p>
        </div>
        <div className="sbProductGrid">
          {products.length === 0 ? (
            <article className="emptyCatalog">No products yet. Run <b>seed_phase2_catalog.py</b>.</article>
          ) : products.map((p) => (
            <article className="sbProductCard" key={p.id}>
              <a className="sbProductImage" href={`/products/${p.slug || p.id}`}>
                {p.image_url ? <img src={p.image_url} alt={p.name} /> : <span>No image</span>}
              </a>
              <small>{p.brand}</small>
              <h3>{p.name}</h3>
              <div className="sbPrice">{formatMoney(p.price)}</div>
              <ProductActions productId={p.id} />
            </article>
          ))}
        </div>
        <div className="sbShowMore"><a href="/products">SHOW MORE</a></div>
      </section>

      <section className="sbInstagram" id="instagram">
        <h2>◎ #KGRACEYOUNG</h2>
        <p>Show us your looks and tag @kgraceyoung_us @kgraceyoung_en</p>
      </section>

      <footer className="sbFooter">
        <div className="sbFooterInner">
          <div><h3>SHOP</h3><a>New Arrivals</a><a>Best Sellers</a><a>Shop Instagram</a><a>Sale</a><a>Search</a></div>
          <div><h3>INFORMATION</h3><a>Privacy Policy</a><a>Terms of Service</a><a>Refund Policy</a></div>
          <div><h3>CUSTOMER SERVICE</h3><a>About Us</a><a>FAQs</a><a>Contact Us</a><a>Grow With Us</a></div>
          <div className="sbNewsletter"><h3>STAY CONNECTED</h3><div className="sbSocials"><span>f</span><span>𝕏</span><span>◎</span><span>p</span><span>▶</span><span>♪</span></div><h3>SIGN UP & GET THE INSIDE SCOOP</h3><form><input placeholder="enter your email address"/><button>SUBMIT</button></form></div>
        </div>
        <div className="sbCopyright">
          <p>© 2026 KGRACEYOUNG. All Rights Reserved.</p>
          <p>K Grace Young Beauty Commerce. Seoul · New York · Toronto</p>
        </div>
      </footer>
    </main>
  );
}
