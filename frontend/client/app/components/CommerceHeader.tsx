import AuthHeader from './AuthHeader';

const topMenus = ['SHOP ALL', 'LIP CARE', 'MAKEUP', 'VEGAN🌿', 'ABOUT US', 'VIDEO'];

function SearchIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="10.8" cy="10.8" r="6.6" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="m15.6 15.6 4.8 4.8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export default function CommerceHeader() {
  return (
    <header className="selfHeader">
      <div className="selfHeaderInner">
        <a className="selfLogoLink" href="/" aria-label="Grace Young home">
          <img src="/grace-young-logo-transparent.png" alt="Grace Young" />
        </a>
        <div className="selfHeaderRight">
          <form className="selfSearch" action="/">
            <input name="q" placeholder="Search" />
            <button type="submit" aria-label="Search"><SearchIcon /></button>
          </form>
          <div className="selfShipping">FREE SHIPPING ON ORDERS OVER $70+</div>
          <AuthHeader />
        </div>
      </div>
      <nav className="selfNav" aria-label="Main navigation">
        {topMenus.map((item) => <a href={item === 'VIDEO' ? '#video' : '#best'} key={item}>{item}</a>)}
      </nav>
    </header>
  );
}
