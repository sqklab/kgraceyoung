import ProductActions from '../components/ProductActions';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
type Product={id:string;slug:string;name:string;brand?:string;price:number;currency:string;image_url?:string};
async function getProducts():Promise<Product[]>{try{const r=await fetch(`${API}/api/v1/catalog/products?limit=250`,{cache:'no-store'});return r.ok?await r.json():[]}catch{return []}}
function money(v:number){return `$${Number(v||0).toFixed(2)}`}
export default async function ProductsPage(){const products=await getProducts();return <main className="commercePage"><a href="/">← Grace Young</a><h1>Shop All</h1><p className="muted">{products.length} products available.</p><div className="sbProductGrid productListingGrid">{products.map((p)=>{return <article className="sbProductCard" key={p.id}><a href={`/products/${p.slug}`} className="sbProductImage">{p.image_url?<img className="sbImagePrimary" src={p.image_url} alt={p.name}/>:<span>No image</span>}</a><small>{p.brand}</small><a href={`/products/${p.slug}`}><h3>{p.name}</h3></a><div className="sbPrice">{money(p.price)}</div><ProductActions productId={p.id}/></article>})}</div></main>}
