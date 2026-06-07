import './styles.css';
export const metadata = { title: 'Grace Young Admin', description: 'Back Office' };
export default function RootLayout({ children }: { children: React.ReactNode }) { return <html lang="en"><body>{children}</body></html>; }
