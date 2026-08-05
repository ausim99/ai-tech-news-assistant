"use client";

import { getStatus } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState } from "@/components/error-state";
import { Skeleton } from "@/components/skeleton";
import { StatCard } from "@/components/stat-card";

export default function UsagePage() {
  const { data, loading, error, refetch } = useApi(getStatus);
  const analytics = data?.analytics;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Usage &amp; Reliability</h1>

      <p className="text-sm text-muted">
        Tracks pipeline run reliability from the last {analytics?.total_runs_logged ?? "…"} logged runs.
        Per-provider API call/cost metering (Grok, Telegram, WhatsApp) isn&apos;t implemented yet.
      </p>

      {loading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      )}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {analytics && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <StatCard label="Runs logged" value={analytics.total_runs_logged} />
          <StatCard label="Successful runs" value={analytics.successful_runs} />
          <StatCard
            label="Success rate"
            value={analytics.success_rate != null ? `${Math.round(analytics.success_rate * 100)}%` : "n/a"}
            tone={
              analytics.success_rate == null
                ? "default"
                : analytics.success_rate >= 0.9
                  ? "success"
                  : analytics.success_rate >= 0.7
                    ? "warning"
                    : "danger"
            }
          />
          <StatCard
            label="Last run items"
            value={analytics.last_run?.item_count ?? "n/a"}
            hint={analytics.last_run ? new Date(analytics.last_run.timestamp).toLocaleString() : undefined}
          />
        </section>
      )}
    </div>
  );
}
