import AuthHeader from './AuthHeader';

const navItems = ['SHOP ALL', 'LIP CARE', 'MAKEUP', 'VEGAN🌿', 'ABOUT US', 'VIDEO'];

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="10.8" cy="10.8" r="6.8" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="m16 16 4.4 4.4" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  );
}

export default function CommerceHeader() {
  return (
    <header className="sbHeader">
      <div className="sbHeaderInner">
        <a className="sbLogoLink" href="/" aria-label="kgraceyoung home">
          <img src="/kgraceyoung-logo-transparent.png" alt="kgraceyoung" />
        </a>

        <div className="sbHeaderRight">
          <form className="sbSearch" action="/">
            <input name="q" placeholder="Search" aria-label="Search" />
            <button type="submit" aria-label="Search"><SearchIcon /></button>
          </form>
          <div className="sbShipping">FREE SHIPPING ON ORDERS OVER $70+</div>
          <AuthHeader />
        </div>
      </div>
      <nav className="sbNav" aria-label="Main navigation">
        {navItems.map((item) => (
          <a key={item} href={item === 'VIDEO' ? '#instagram' : '#products'}>{item}</a>
        ))}
      </nav>
    </header>
  );
}
