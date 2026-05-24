import CommerceHeader from './components/CommerceHeader';
import ProductActions from './components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

const heroSlides = [
  { image: '/hero/grace-slide-01.png', title: 'Total Skin Rejuvenation' },
  { image: '/hero/grace-slide-02.png', title: 'Botanical Daily Ritual' },
  { image: '/hero/grace-slide-03.png', title: 'Clean Clinical Essentials' },
  { image: '/hero/grace-slide-04.png', title: 'Private Label Beauty' },
  { image: '/hero/grace-slide-05.png', title: 'Sunlit Body Care' },
  { image: '/hero/grace-slide-06.png', title: 'Warm Botanical Skincare' },
  { image: '/hero/grace-slide-07.png', title: 'Brightening Treatment Set' },
  { image: '/hero/grace-slide-08.png', title: 'Fresh Leaf Moisture' },
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
              <img src={slide.image} alt={slide.title} />
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
          ) : products.map((p, index) => {
            const hover = products[(index + 1) % products.length]?.image_url;
            return (
              <article className="sbProductCard" key={p.id}>
                <div className="sbProductImage">
                  {p.image_url ? (
                    <>
                      <img className="sbImagePrimary" src={p.image_url} alt={p.name} />
                      {hover && hover !== p.image_url ? <img className="sbImageHover" src={hover} alt="" aria-hidden="true" /> : null}
                    </>
                  ) : <span>No image</span>}
                </div>
                <small>{p.brand}</small>
                <h3>{p.name}</h3>
                <div className="sbPrice">{formatMoney(p.price)}</div>
                <ProductActions productId={p.id} />
              </article>
            );
          })}
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
