"use client";

import { getConfig } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";

export default function SourcesPage() {
  const { data, loading, error, refetch } = useApi(getConfig);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Sources</h1>

      {loading && <ListSkeleton count={6} />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <div className="rounded-lg border border-border bg-card overflow-hidden overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-background text-muted text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Source</th>
                <th className="px-4 py-2 font-medium">Category</th>
                <th className="px-4 py-2 font-medium">Feed</th>
                <th className="px-4 py-2 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.sources.map((source) => (
                <tr key={source.name} className="border-t border-border">
                  <td className="px-4 py-2 font-medium">{source.name}</td>
                  <td className="px-4 py-2">{source.category}</td>
                  <td className="px-4 py-2 max-w-xs truncate">
                    {source.rss_url ? (
                      <a
                        href={source.rss_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-accent hover:underline"
                      >
                        {source.rss_url}
                      </a>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td className="px-4 py-2">
                    {source.rss_url ? (
                      <span className="text-success">active</span>
                    ) : (
                      <span className="text-warning" title={source.note}>
                        {source.status ?? "unavailable"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
