import type { Metadata } from 'next';
import './styles.css';

export const metadata: Metadata = {
  title: 'kgraceyoung | K-Beauty Commerce',
  description: 'kgraceyoung beauty commerce for curated K-beauty routines and products.',
  icons: { icon: '/favicon.ico' }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
