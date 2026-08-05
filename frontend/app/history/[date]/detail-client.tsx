"use client";

import Link from "next/link";
import { getByDate } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { NewsItemCard } from "@/components/news-item-card";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { ExportJsonButton } from "@/components/export-json-button";

export function HistoryDetailClient({ date }: { date: string }) {
  const { data, loading, error, notFound, refetch } = useApi(() => getByDate(date), [date]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <Link href="/history" className="text-sm text-accent hover:underline">
            ← History
          </Link>
          <h1 className="text-xl font-semibold mt-1">{date}</h1>
        </div>
        {data && <ExportJsonButton data={data} filename={`digest-${date}.json`} />}
      </div>

      {loading && <ListSkeleton count={5} />}
      {notFound && <EmptyState message={`No digest found for ${date}.`} />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          <section className="space-y-3">
            <h2 className="font-medium">🤖 Top AI News</h2>
            <div className="grid gap-3">
              {data.top_ai_news.map((item) => (
                <NewsItemCard key={item.link} item={item} />
              ))}
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="font-medium">💻 Top Tech News</h2>
            <div className="grid gap-3">
              {data.top_tech_news.map((item) => (
                <NewsItemCard key={item.link} item={item} />
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
