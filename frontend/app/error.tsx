"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="rounded-lg border border-danger/30 bg-danger/5 p-8 text-center space-y-3">
      <p className="text-danger">⚠️ Something went wrong: {error.message}</p>
      <button
        onClick={reset}
        className="rounded-md border border-border px-3 py-1.5 text-sm hover:bg-card transition-colors"
      >
        Try again
      </button>
    </div>
  );
}
