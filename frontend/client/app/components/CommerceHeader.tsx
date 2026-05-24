import AuthHeader from './AuthHeader';

const categories = ['SHOP ALL', 'SKINCARE', 'SUNCARE', 'DEVICES', 'REELS', 'BRANDS'];

function SearchIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="10.7" cy="10.7" r="6.7" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="m15.7 15.7 5 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export default function CommerceHeader() {
  return (
    <header className="selfHeaderWrap">
      <div className="selfTopHeader">
        <a className="selfLogo" href="/" aria-label="Grace Young home">GRACE YOUNG</a>
        <div className="selfRightStack">
          <form className="selfSearchBox" action="/">
            <input name="q" placeholder="Search" />
            <button type="submit" aria-label="Search"><SearchIcon /></button>
          </form>
          <div className="selfShippingText">FREE SHIPPING ON ORDERS OVER $70+</div>
          <AuthHeader />
        </div>
      </div>
      <nav className="selfMenuBar" aria-label="Main categories">
        {categories.map((c, idx) => <a className={idx === 0 ? 'active' : ''} href="/#best" key={c}>{c}</a>)}
      </nav>
    </header>
  );
}
