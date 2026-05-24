import CommerceHeader from '../components/CommerceHeader';
import ProductActions from '../components/ProductActions';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id: string; slug: string; name: string; brand: string; price: number; currency: string; image_url?: string; description?: string };

async function getProducts(): Promise<Product[]> {
  try {
    const res = await fetch(`${API}/api/v1/catalog/products?limit=250`, { cache: 'no-store' });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

function formatMoney(value: number) {
  return `$${Number(value || 0).toFixed(2)}`;
}

export default async function ProductsPage() {
  const products = await getProducts();
  return (
    <main className="sbShell">
      <CommerceHeader />
      <section className="sbProductSection sbProductListing" id="products">
        <div className="sbSectionTitle">
          <h2>SHOP ALL</h2>
          <p>{products.length} products</p>
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
      </section>
    </main>
  );
}
