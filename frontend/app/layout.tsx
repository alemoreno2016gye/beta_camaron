import './globals.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <main>
          <h1>ALTAMA Shrimp Intelligence</h1>
          <nav className="nav">
            <Link href="/">Home</Link>
            <Link href="/alerts">Alerts Center</Link>
            <Link href="/reports">Reports</Link>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
