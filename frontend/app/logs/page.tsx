"use client";

import { getLogs } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { ExportJsonButton } from "@/components/export-json-button";

function statusTone(status: string): string {
  if (status === "ok") return "text-success";
  if (status === "empty") return "text-warning";
  return "text-danger";
}

export default function LogsPage() {
  const { data, loading, error, refetch } = useApi(getLogs);
  const sorted = [...(data ?? [])].reverse();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Logs</h1>
        {data && <ExportJsonButton data={data} filename="logs.json" />}
      </div>

      {loading && <ListSkeleton count={6} />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && sorted.length === 0 && <EmptyState message="No pipeline runs logged yet." />}

      {sorted.length > 0 && (
        <div className="rounded-lg border border-border bg-card overflow-hidden overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-background text-muted text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Timestamp (UTC)</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Items</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((entry, i) => (
                <tr key={i} className="border-t border-border">
                  <td className="px-4 py-2 whitespace-nowrap">
                    {new Date(entry.timestamp).toLocaleString()}
                  </td>
                  <td className={`px-4 py-2 font-medium ${statusTone(entry.status)}`}>{entry.status}</td>
                  <td className="px-4 py-2">{entry.item_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
