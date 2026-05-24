import AuthHeader from './AuthHeader';

const categories = ['Beauty', 'Best', 'New', 'Brands', 'Skincare', 'Makeup', 'Body', 'Hair', 'Face Masks', 'Suncare', 'K-Pop'];

export default function CommerceHeader() {
  return (
    <header className="kurlyHeaderWrap">
      <section className="utilityBar">Free shipping over US$49 · English / Français / Español / 한국어</section>
      <div className="mainHeaderKurly">
        <a className="brandLogoKurly" href="/">GRACE YOUNG</a>
        <form className="searchBoxKurly" action="/">
          <input name="q" placeholder="Search for a product or brand..." />
          <button type="submit" aria-label="Search">⌕</button>
        </form>
        <AuthHeader />
      </div>
      <nav className="categoryNavKurly">
        <button className="hamburgerKurly" aria-label="Open categories">☰</button>
        {categories.map((c) => <a href="/#best" key={c}>{c}</a>)}
        <a className="membershipLink" href="/account">Membership</a>
      </nav>
    </header>
  );
}
