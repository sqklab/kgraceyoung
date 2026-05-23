import type { Metadata } from 'next';
import './styles.css';

export const metadata: Metadata = {
  title: 'Grace Young | K-Beauty Video Commerce',
  description: 'Watch K-Beauty reels, discover curated routines, and shop trusted Korean beauty.',
  icons: { icon: '/favicon.ico' }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
