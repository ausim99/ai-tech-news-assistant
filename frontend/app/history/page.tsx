"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { getHistory } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { Pagination } from "@/components/pagination";

const PAGE_SIZE = 14;

export default function HistoryPage() {
  const { data, loading, error, refetch } = useApi(getHistory);
  const [page, setPage] = useState(1);

  const sorted = useMemo(() => [...(data ?? [])].sort((a, b) => (a.date < b.date ? 1 : -1)), [data]);
  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">History</h1>

      {loading && <ListSkeleton count={6} />}
      {error && <ErrorState message={error} onRetry={refetch} />}
      {!loading && !error && sorted.length === 0 && <EmptyState message="No digest history yet." />}

      {pageItems.length > 0 && (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-background text-muted text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Date</th>
                <th className="px-4 py-2 font-medium">Top AI</th>
                <th className="px-4 py-2 font-medium">Top Tech</th>
              </tr>
            </thead>
            <tbody>
              {pageItems.map((entry) => (
                <tr key={entry.date} className="border-t border-border hover:bg-background">
                  <td className="px-4 py-2">
                    <Link href={`/history/${entry.date}`} className="text-accent hover:underline">
                      {entry.date}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{entry.top_ai_count}</td>
                  <td className="px-4 py-2">{entry.top_tech_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </div>
  );
}
