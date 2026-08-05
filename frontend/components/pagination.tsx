export function Pagination({
  page,
  totalPages,
  onChange,
}: {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
}) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2 pt-4">
      <button
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="rounded-md border border-border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-card"
      >
        ← Prev
      </button>
      <span className="text-sm text-muted">
        Page {page} of {totalPages}
      </span>
      <button
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="rounded-md border border-border px-3 py-1.5 text-sm disabled:opacity-40 hover:bg-card"
      >
        Next →
      </button>
    </div>
  );
}
