import type { Metadata } from 'next';
import './styles.css';
export const metadata: Metadata = { title: 'Grace Young Admin', icons: { icon: '/favicon.ico' } };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
