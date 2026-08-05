import Link from "next/link";

export default function NotFound() {
  return (
    <div className="rounded-lg border border-dashed border-border p-8 text-center space-y-3">
      <p className="text-muted">Page not found.</p>
      <Link href="/" className="text-accent hover:underline text-sm">
        ← Back home
      </Link>
    </div>
  );
}
