import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Sans_Bengali } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/nav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const notoBangla = Noto_Sans_Bengali({
  variable: "--font-noto-bangla",
  subsets: ["bengali"],
});

export const metadata: Metadata = {
  title: "AI Tech News Assistant",
  description: "Daily AI & tech digest dashboard - Bangla summaries, tutorials, and delivery status.",
};

const NO_FLASH_SCRIPT = `
try {
  var stored = localStorage.getItem('theme');
  var dark = stored ? stored === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.classList.toggle('dark', dark);
} catch (e) {}
`;

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${notoBangla.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <script dangerouslySetInnerHTML={{ __html: NO_FLASH_SCRIPT }} />
        <Nav />
        <main className="flex-1 w-full max-w-6xl mx-auto px-4 py-6 sm:px-6">{children}</main>
        <footer className="border-t border-border py-4 text-center text-xs text-muted">
          AI Tech News Assistant
        </footer>
      </body>
    </html>
  );
}
