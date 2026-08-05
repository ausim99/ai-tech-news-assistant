"use client";

import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getToday } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import { ErrorState, EmptyState } from "@/components/error-state";
import { Skeleton } from "@/components/skeleton";
import { categoryEmoji } from "@/lib/category";

export default function CategoriesPage() {
  const { data, loading, error, notFound, refetch } = useApi(getToday);

  const counts = useMemo(() => {
    const map = new Map<string, number>();
    for (const item of data?.items ?? []) {
      const cat = item.category || "Other";
      map.set(cat, (map.get(cat) ?? 0) + 1);
    }
    return Array.from(map.entries())
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  }, [data]);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-semibold">Categories{data ? ` — ${data.date}` : ""}</h1>

      {loading && <Skeleton className="h-72" />}
      {notFound && <EmptyState message="No digest generated for today yet." />}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {counts.length > 0 && (
        <>
          <div className="rounded-lg border border-border bg-card p-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={counts} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                <XAxis type="number" allowDecimals={false} stroke="var(--muted)" fontSize={12} />
                <YAxis type="category" dataKey="category" stroke="var(--muted)" fontSize={12} width={110} />
                <Tooltip
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="count" fill="var(--accent)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {counts.map(({ category, count }) => (
              <div key={category} className="rounded-lg border border-border bg-card p-3 text-sm">
                <div className="text-muted text-xs">
                  {categoryEmoji(category)} {category}
                </div>
                <div className="text-lg font-semibold mt-1">{count}</div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
