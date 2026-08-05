"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ThemeToggle } from "./theme-toggle";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/today", label: "Today" },
  { href: "/history", label: "History" },
  { href: "/workflows", label: "Workflows" },
  { href: "/logs", label: "Logs" },
  { href: "/sources", label: "Sources" },
  { href: "/categories", label: "Categories" },
  { href: "/settings", label: "Settings" },
  { href: "/usage", label: "Usage" },
  { href: "/about", label: "About" },
];

export function Nav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="border-b border-border bg-card sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
        <Link href="/" className="font-semibold whitespace-nowrap">
          🗞️ AI Tech News
        </Link>

        <nav className="hidden md:flex items-center gap-1 overflow-x-auto">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 py-1.5 rounded-md text-sm whitespace-nowrap transition-colors ${
                pathname === link.href
                  ? "bg-accent text-accent-foreground"
                  : "hover:bg-background text-muted"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <button
            className="md:hidden rounded-md border border-border p-2 text-sm"
            onClick={() => setOpen((o) => !o)}
            aria-label="Toggle menu"
            aria-expanded={open}
          >
            {open ? "✕" : "☰"}
          </button>
        </div>
      </div>

      {open && (
        <nav className="md:hidden border-t border-border px-4 py-2 flex flex-col gap-1">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className={`px-3 py-2 rounded-md text-sm ${
                pathname === link.href ? "bg-accent text-accent-foreground" : "hover:bg-background"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
