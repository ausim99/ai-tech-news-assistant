"use client";

import Link from "next/link";
import { getStatus, getToday, runPipeline } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { StatCard } from "@/components/stat-card";
import { NewsItemCard } from "@/components/news-item-card";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton, Skeleton } from "@/components/skeleton";
import { ActionButton } from "@/components/action-button";

export default function HomePage() {
  const status = useApi(getStatus);
  const digest = useApi(getToday);

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Overview</h1>
        <ActionButton
          label="▶ Run pipeline now"
          pendingLabel="Dispatching..."
          onRun={() => runPipeline({})}
        />
      </div>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {status.loading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-20" />)
        ) : status.error ? (
          <div className="col-span-full">
            <ErrorState message={status.error} onRetry={status.refetch} />
          </div>
        ) : (
          <>
            <StatCard
              label="Last run"
              value={status.data?.last_run?.conclusion ?? status.data?.last_run?.status ?? "unknown"}
              tone={
                status.data?.last_run?.conclusion === "success"
                  ? "success"
                  : status.data?.last_run?.conclusion === "failure"
                    ? "danger"
                    : "default"
              }
              hint={status.data?.last_run?.started_at ?? undefined}
            />
            <StatCard
              label="Success rate"
              value={
                status.data?.analytics.success_rate != null
                  ? `${Math.round(status.data.analytics.success_rate * 100)}%`
                  : "n/a"
              }
            />
            <StatCard label="Runs logged" value={status.data?.analytics.total_runs_logged ?? 0} />
            <StatCard
              label="Today's items"
              value={digest.data ? digest.data.items.length : digest.loading ? "…" : 0}
            />
          </>
        )}
      </section>

      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-medium">Today&apos;s top AI news</h2>
          <Link href="/today" className="text-sm text-accent hover:underline">
            View all →
          </Link>
        </div>

        {digest.loading ? (
          <ListSkeleton count={3} />
        ) : digest.notFound ? (
          <EmptyState message="No digest generated for today yet. It runs daily at 06:00 (Asia/Dhaka)." />
        ) : digest.error ? (
          <ErrorState message={digest.error} onRetry={digest.refetch} />
        ) : digest.data && digest.data.top_ai_news.length > 0 ? (
          <div className="grid gap-3">
            {digest.data.top_ai_news.slice(0, 3).map((item) => (
              <NewsItemCard key={item.link} item={item} />
            ))}
          </div>
        ) : (
          <EmptyState message="No AI news selected for today." />
        )}
      </section>
    </div>
  );
}
