import CommerceHeader from './components/CommerceHeader';
import ProductActions from './components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

const heroSlides = [
  { image: 'https://source.unsplash.com/1800x620/?lip-balm,cosmetics,pastel&sig=201', label: 'VEGAN LIP MASK 🌿', title: 'Cracked Lip Repair', cta: 'SHOP NOW' },
  { image: 'https://source.unsplash.com/1800x620/?korean,skincare,cosmetics&sig=202', label: 'K-BEAUTY DAILY CARE', title: 'Gentle glow for every routine', cta: 'SHOP NOW' },
  { image: 'https://source.unsplash.com/1800x620/?serum,skincare,pastel&sig=203', label: 'SERUM EDIT', title: 'Layer soft hydration and glow', cta: 'DISCOVER' },
  { image: 'https://source.unsplash.com/1800x620/?sunscreen,beauty,cream&sig=204', label: 'SUN CARE', title: 'Light SPF picks for daily protection', cta: 'SHOP SPF' },
  { image: 'https://source.unsplash.com/1800x620/?makeup,lipstick,pink&sig=205', label: 'MAKEUP', title: 'Soft color, clean finish', cta: 'SHOP MAKEUP' },
  { image: 'https://source.unsplash.com/1800x620/?sheet-mask,skincare&sig=206', label: 'MASK BAR', title: 'Quick glow care for busy days', cta: 'SHOP MASKS' },
  { image: 'https://source.unsplash.com/1800x620/?haircare,beauty,bottle&sig=207', label: 'HAIR CARE', title: 'Scalp-first healthy shine', cta: 'SHOP HAIR' },
  { image: 'https://source.unsplash.com/1800x620/?body-lotion,cosmetics&sig=208', label: 'BODY CARE', title: 'Soft skin from head to toe', cta: 'SHOP BODY' },
  { image: 'https://source.unsplash.com/1800x620/?beauty-device,skincare&sig=209', label: 'DEVICES', title: 'Home beauty tools for better rituals', cta: 'SHOP DEVICES' },
  { image: 'https://source.unsplash.com/1800x620/?perfume,cosmetics,clean&sig=210', label: 'FRAGRANCE', title: 'Clean mood and soft finish', cta: 'SHOP SCENT' },
  { image: 'https://source.unsplash.com/1800x620/?organic,beauty,spa&sig=211', label: 'CLEAN BEAUTY', title: 'Ingredient-led gentle essentials', cta: 'SHOP CLEAN' },
];

async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${API}/api/v1/catalog/products?limit=8`, { cache: 'no-store' });
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
    <main className="selfBeautyShell">
      <CommerceHeader />

      <section className="selfHero" aria-label="Grace Young beauty promotions">
        <div className="selfSlideTrack">
          {heroSlides.map((slide, index) => (
            <article className="selfSlide" key={slide.title} aria-hidden={index !== 0}>
              <img src={slide.image} alt="" />
              <div className="selfSlideCopy">
                <h1>{slide.label}</h1>
                <div className="selfDivider" />
                <p>{slide.title}</p>
                <a href="#best">{slide.cta}</a>
              </div>
            </article>
          ))}
        </div>
        <button className="selfArrow left" aria-label="Previous slide">‹</button>
        <button className="selfArrow right" aria-label="Next slide">›</button>
        <div className="selfDots" aria-hidden="true">{heroSlides.slice(0, 3).map((_, i) => <span key={i} className={i === 0 ? 'active' : ''} />)}</div>
      </section>

      <section className="selfProductSection" id="best">
        <div className="selfSectionTitle">
          <h2>VEGAN LIP MASK 🌿</h2>
          <p>Cracked Lip Repair</p>
        </div>
        <div className="selfProductGrid">
          {products.length === 0 ? <article className="emptyCatalog">No products yet. Run <b>seed_phase2_catalog.py</b>.</article> : products.slice(0, 4).map((p) => (
            <article className="selfProductCard" key={p.id}>
              <div className="selfProductImage">{p.image_url ? <img src={p.image_url} alt={p.name} /> : <span>No image</span>}</div>
              <h3>{p.name}</h3>
              <div className="selfPrice">{formatMoney(p.price)}</div>
              <ProductActions productId={p.id} />
            </article>
          ))}
        </div>
      </section>

      <section className="selfInstagram" id="video">
        <h2>◎ #GRACEYOUNG</h2>
        <p>Show us your looks and tag @graceyoung_beauty @graceyoung_us</p>
      </section>

      <footer className="selfFooter">
        <div className="selfFooterInner">
          <div><h3>SHOP</h3><a>New Arrivals</a><a>Best Sellers</a><a>Shop Instagram</a><a>Sale</a><a>Search</a></div>
          <div><h3>INFORMATION</h3><a>Privacy Policy</a><a>Terms of Service</a><a>Refund Policy</a></div>
          <div><h3>CUSTOMER SERVICE</h3><a>About Us</a><a>FAQs</a><a>Contact Us</a><a>Grow With Us</a></div>
          <div className="newsletter"><h3>STAY CONNECTED</h3><div className="socials"><span>f</span><span>𝕏</span><span>◎</span><span>p</span><span>▶</span><span>♪</span></div><h3>SIGN UP & GET THE INSIDE SCOOP</h3><form><input placeholder="enter your email address"/><button>SUBMIT</button></form></div>
        </div>
        <div className="selfCopyright">
          <p>© 2026 GRACE YOUNG. GET YOUR BEAUTITUDE. All Rights Reserved.</p>
          <p>Grace Young Beauty Commerce. Seoul · New York · Toronto</p>
        </div>
      </footer>
    </main>
  );
}
