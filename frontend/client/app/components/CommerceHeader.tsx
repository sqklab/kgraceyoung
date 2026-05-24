import AuthHeader from './AuthHeader';

const topMenus = ['Best', 'Brand Pavilion', 'body', 'Reels'];
const categoryRows = [
  { icon: '🧴', label: 'skincare', active: false, subs: ['Toner', 'Serum / Ampoule', 'Cream', 'Cleanser', 'Eye care'] },
  { icon: '🪞', label: 'makeup', active: false, subs: ['Cushion', 'Lip tint', 'Blush', 'Primer', 'Brow'] },
  { icon: '🫧', label: 'Cleansing', active: false, subs: ['Cleansing oil', 'Foam cleanser', 'Cleansing balm', 'Peeling pad'] },
  { icon: '☀️', label: 'Sun care', active: true, subs: ['sunstick', 'Sun cushion', 'sunscreen', 'Soothing/After-sun', 'Pre-patch'] },
  { icon: '🧼', label: 'Body care', active: false, subs: ['Body lotion', 'Body scrub', 'Body sun care', 'Hand cream'] },
  { icon: '✂️', label: 'Hair care', active: false, subs: ['Shampoo', 'Treatment', 'Scalp care', 'Hair device'] },
  { icon: '🪥', label: 'Oral hygiene products', active: false, subs: ['Toothpaste', 'Mouth wash', 'Whitening care'] },
  { icon: '➕', label: 'Dermo-cosmetics', active: false, subs: ['Sensitive care', 'Barrier care', 'Trouble care'] },
  { icon: '🍃', label: 'Perfume · Diffuser', active: false, subs: ['Perfume', 'Body mist', 'Diffuser'] },
  { icon: '👶', label: 'Toddlers', active: false, subs: ['Baby lotion', 'Mild wash', 'Kids sun care'] },
  { icon: '🪒', label: 'male', active: false, subs: ['Men cleanser', 'Shaving', 'Men hair care'] },
  { icon: '✨', label: 'Luxury Beauty', active: false, subs: ['Premium serum', 'Luxury cream', 'Device set'] },
];

function SearchIcon() {
  return (
    <svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="10.7" cy="10.7" r="6.7" fill="none" stroke="currentColor" strokeWidth="2.2" />
      <path d="m15.7 15.7 5 5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg width="42" height="42" viewBox="0 0 44 44" aria-hidden="true">
      <path d="M7 12h30M7 22h30M7 32h30" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export default function CommerceHeader() {
  return (
    <header className="sbHeaderWrap">
      <div className="sbMainHeader">
        <a className="sbLogo" href="/" aria-label="Grace Young home">GRACE YOUNG</a>
        <div className="sbRight">
          <form className="sbSearch" action="/">
            <input name="q" placeholder="Search" />
            <button type="submit" aria-label="Search"><SearchIcon /></button>
          </form>
          <div className="sbShipping">FREE SHIPPING ON ORDERS OVER $70+</div>
          <AuthHeader />
        </div>
      </div>
      <nav className="sbNav" aria-label="Main navigation">
        <div className="sbCategoryWrap">
          <button className="sbCategoryButton" type="button"><MenuIcon /> <span>Category</span></button>
          <div className="sbMegaMenu">
            <div className="sbMegaLeft">
              {categoryRows.map((row) => (
                <a className={row.active ? 'active' : ''} href="#best" key={row.label}>
                  <span className="sbMegaIcon">{row.icon}</span>
                  <span>{row.label}</span>
                </a>
              ))}
            </div>
            <div className="sbMegaRight">
              {(categoryRows.find((row) => row.active) || categoryRows[0]).subs.map((sub) => <a href="#best" key={sub}>{sub}</a>)}
            </div>
          </div>
        </div>
        {topMenus.map((item) => <a href="#best" key={item}>{item}</a>)}
      </nav>
    </header>
  );
}
