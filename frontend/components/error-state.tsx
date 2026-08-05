export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-lg border border-danger/30 bg-danger/5 p-6 text-center space-y-3">
      <p className="text-danger text-sm">⚠️ {message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded-md border border-border px-3 py-1.5 text-sm hover:bg-card transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-border p-8 text-center text-muted text-sm">
      {message}
    </div>
  );
}
