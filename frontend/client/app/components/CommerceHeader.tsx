import AuthHeader from './AuthHeader';

const categories = ['In-Store', 'Best', 'New', 'Brands', 'Skincare', 'Makeup', 'Body', 'Hair', 'Face Masks', 'Suncare', 'K-Beauty Devices'];

export default function CommerceHeader() {
  return (
    <>
      <section className="utilityBar">Free shipping over US$49 · SAVE US$20 with GRACE YOUNG APP! · English / Français / Español / 한국어</section>
      <header className="commerceHeader">
        <a className="brandLogo" href="/">GRACE YOUNG</a>
        <form className="searchBox" action="/">
          <input name="q" placeholder="Search for a product or brand..." />
          <button type="submit" aria-label="Search">⌕</button>
        </form>
        <AuthHeader />
      </header>
      <nav className="categoryNav">
        <button className="hamburger" aria-label="Open categories">☰</button>
        {categories.map((c) => <a href={c === 'Face Masks' ? '/#face-masks' : '/'} key={c}>{c}</a>)}
        <a className="membershipLink" href="/account">Membership</a>
      </nav>
      <section className="benefitStrip">
        <span>✈ Free shipping over US$49</span>
        <span>▣ Reels commerce ready</span>
        <span>♡ Grace Rewards points</span>
      </section>
    </>
  );
}
