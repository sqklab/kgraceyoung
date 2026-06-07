import ProductActions from '../../components/ProductActions';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Product = { id:string; slug:string; name:string; brand?:string; price:number; currency:string; description?:string; image_url?:string; images:{url:string; alt_text?:string}[]; ingredients?:string; how_to_use?:string; shipping_note?:string; related?:Product[] };

async function getProduct(slug:string):Promise<Product|null>{
  try{ const res=await fetch(`${API}/api/v1/catalog/products/${slug}`,{cache:'no-store'}); if(!res.ok)return null; return res.json(); }catch{return null;}
}
function money(v:number){return `$${Number(v||0).toFixed(2)}`}
export default async function ProductDetail({params}:{params:{slug:string}}){
  const p=await getProduct(params.slug);
  if(!p) return <main className="commercePage"><a href="/products">← Products</a><h1>Product not found</h1></main>;
  const images=p.images?.length?p.images:[{url:p.image_url||'', alt_text:p.name}];
  return <main className="commercePage productDetailPage">
    <a href="/products">← Products</a>
    <section className="pdpGrid">
      <div className="pdpGallery">
        <img className="pdpMainImage" src={images[0].url} alt={p.name}/>
        <div className="pdpThumbs">{images.slice(0,4).map((img,i)=><img key={i} src={img.url} alt={img.alt_text||p.name}/>)}</div>
      </div>
      <div className="pdpInfo">
        <p className="pdpBrand">{p.brand}</p>
        <h1>{p.name}</h1>
        <p className="pdpDesc">{p.description}</p>
        <div className="pdpPrice">{money(p.price)}</div>
        <ProductActions productId={p.id}/>
        <div className="pdpMeta"><b>Free shipping over $70+</b><span>Ships from Grace Young fulfillment.</span></div>
      </div>
    </section>
    <section className="pdpTabs">
      <article><h2>Description</h2><p>{p.description}</p></article>
      <article><h2>Ingredients</h2><p>{p.ingredients}</p></article>
      <article><h2>How to use</h2><p>{p.how_to_use}</p></article>
      <article><h2>Shipping</h2><p>{p.shipping_note}</p></article>
    </section>
    {p.related?.length ? <section className="sbProductSection"><div className="sbSectionTitle"><h2>You may also like</h2></div><div className="sbProductGrid">{p.related.map((r)=><a className="sbProductCard" key={r.id} href={`/products/${r.slug}`}><div className="sbProductImage">{r.image_url&&<img src={r.image_url} alt={r.name}/>}</div><h3>{r.name}</h3><div className="sbPrice">{money(r.price)}</div></a>)}</div></section> : null}
  </main>;
}
