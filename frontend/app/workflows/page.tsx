"use client";

import { useState } from "react";
import { getWorkflows, resendDigest, runPipeline } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { ActionButton } from "@/components/action-button";

const WORKFLOW_LABELS: Record<string, string> = {
  "pipeline.yml": "Daily Pipeline",
  "manual-run.yml": "Manual Run",
  "healthcheck.yml": "Health Check",
  "cleanup.yml": "Cleanup",
};

function statusTone(conclusion: string | null, status: string): string {
  if (status === "in_progress" || status === "queued") return "text-warning";
  if (conclusion === "success") return "text-success";
  if (conclusion === "failure" || conclusion === "timed_out") return "text-danger";
  return "text-muted";
}

export default function WorkflowsPage() {
  const { data, loading, error, refetch } = useApi(getWorkflows);
  const [skipSend, setSkipSend] = useState(false);
  const [dryRun, setDryRun] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Workflow Monitor</h1>
        <ActionButton label="↻ Refresh" pendingLabel="…" onRun={() => Promise.resolve(refetch())} variant="secondary" />
      </div>

      <div className="rounded-lg border border-border bg-card p-4 space-y-3">
        <h2 className="font-medium text-sm">Trigger a run</h2>
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <label className="flex items-center gap-1.5">
            <input type="checkbox" checked={skipSend} onChange={(e) => setSkipSend(e.target.checked)} />
            Skip Telegram/Gmail send
          </label>
          <label className="flex items-center gap-1.5">
            <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} />
            Dry run (no commit)
          </label>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ActionButton
            label="▶ Run pipeline"
            pendingLabel="Dispatching..."
            onRun={() => runPipeline({ skip_send: skipSend, dry_run: dryRun })}
          />
          <ActionButton
            label="🔁 Resend today's digest"
            pendingLabel="Sending..."
            onRun={resendDigest}
            variant="secondary"
          />
        </div>
      </div>

      {loading && <ListSkeleton count={4} />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <div className="grid md:grid-cols-2 gap-4">
          {Object.entries(data).map(([file, runs]) => (
            <div key={file} className="rounded-lg border border-border bg-card p-4 space-y-2">
              <h2 className="font-medium">{WORKFLOW_LABELS[file] ?? file}</h2>
              {runs.length === 0 ? (
                <EmptyState message="No runs yet." />
              ) : (
                <ul className="space-y-1.5 text-sm">
                  {runs.map((run) => (
                    <li key={run.id} className="flex items-center justify-between gap-2">
                      <a
                        href={run.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`hover:underline ${statusTone(run.conclusion, run.status)}`}
                      >
                        {run.conclusion ?? run.status}
                      </a>
                      <span className="text-muted text-xs">
                        {new Date(run.run_started_at).toLocaleString()}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
