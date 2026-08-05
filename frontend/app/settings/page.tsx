"use client";

import { getConfig } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { StatCard } from "@/components/stat-card";

export default function SettingsPage() {
  const { data, loading, error, refetch } = useApi(getConfig);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Settings</h1>

      <div className="rounded-lg border border-warning/30 bg-warning/5 p-4 text-sm">
        Read-only for now. Schedules, source list, and prompts live in{" "}
        <code className="text-xs bg-background px-1 py-0.5 rounded">data/config.json</code>,{" "}
        <code className="text-xs bg-background px-1 py-0.5 rounded">.github/workflows/</code> and{" "}
        <code className="text-xs bg-background px-1 py-0.5 rounded">prompts/</code> in the repo. Editing
        from here would mean committing to those files via the GitHub API - not wired up yet.
      </div>

      {loading && <ListSkeleton count={3} />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          <section className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <StatCard label="Tutorials generated per run (max)" value={data.max_tutorial_items} />
            <StatCard label="Configured sources" value={data.sources.length} />
            <StatCard
              label="Active sources"
              value={data.sources.filter((s) => s.rss_url).length}
            />
          </section>

          <section className="rounded-lg border border-border bg-card p-4 space-y-2 text-sm">
            <h2 className="font-medium mb-1">Schedule</h2>
            {Object.entries(data.schedule).map(([job, cron]) => (
              <p key={job}>
                <span className="font-medium capitalize">{job}:</span>{" "}
                <code className="text-xs bg-background px-1 py-0.5 rounded">{cron}</code>
              </p>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
