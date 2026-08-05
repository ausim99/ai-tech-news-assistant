"use client";

import { useMemo, useState } from "react";
import { getToday, resendDigest, runPipeline } from "@/lib/api";
import { useApi } from "@/lib/useApi";
import type { NewsItem } from "@/lib/types";
import { NewsItemCard } from "@/components/news-item-card";
import { SearchFilterBar } from "@/components/search-filter-bar";
import { ErrorState, EmptyState } from "@/components/error-state";
import { ListSkeleton } from "@/components/skeleton";
import { ExportJsonButton } from "@/components/export-json-button";
import { ActionButton } from "@/components/action-button";

export default function TodayPage() {
  const { data, loading, error, notFound, refetch } = useApi(getToday);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");

  const categories = useMemo(
    () => Array.from(new Set(data?.items.map((i) => i.category).filter(Boolean) ?? [])),
    [data],
  );

  const filterItems = (items: NewsItem[]) =>
    items.filter((item) => {
      const matchesSearch =
        !search ||
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        (item.title_bn ?? "").includes(search);
      const matchesCategory = !category || item.category === category;
      return matchesSearch && matchesCategory;
    });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-xl font-semibold">Today&apos;s News{data ? ` — ${data.date}` : ""}</h1>
        <div className="flex items-center gap-2">
          {data && <ExportJsonButton data={data} filename={`digest-${data.date}.json`} />}
          <ActionButton label="↻ Refresh" pendingLabel="…" onRun={() => Promise.resolve(refetch())} variant="secondary" />
          <ActionButton label="🔁 Resend" pendingLabel="Sending..." onRun={resendDigest} variant="secondary" />
          <ActionButton label="▶ Run now" pendingLabel="Dispatching..." onRun={() => runPipeline({})} />
        </div>
      </div>

      {loading && <ListSkeleton count={5} />}
      {notFound && (
        <EmptyState message="No digest generated for today yet. It runs daily at 06:00 (Asia/Dhaka), or trigger a manual run above." />
      )}
      {error && <ErrorState message={error} onRetry={refetch} />}

      {data && (
        <>
          <SearchFilterBar
            search={search}
            onSearchChange={setSearch}
            category={category}
            onCategoryChange={setCategory}
            categories={categories}
          />

          <section className="space-y-3">
            <h2 className="font-medium">🤖 Top AI News</h2>
            <div className="grid gap-3">
              {filterItems(data.top_ai_news).map((item) => (
                <NewsItemCard key={item.link} item={item} />
              ))}
              {filterItems(data.top_ai_news).length === 0 && <EmptyState message="No matching AI news." />}
            </div>
          </section>

          <section className="space-y-3">
            <h2 className="font-medium">💻 Top Tech News</h2>
            <div className="grid gap-3">
              {filterItems(data.top_tech_news).map((item) => (
                <NewsItemCard key={item.link} item={item} />
              ))}
              {filterItems(data.top_tech_news).length === 0 && (
                <EmptyState message="No matching tech news." />
              )}
            </div>
          </section>

          <section className="rounded-lg border border-border bg-card p-4 space-y-2 text-sm">
            <h2 className="font-medium mb-1">✨ Today&apos;s Extras</h2>
            <Extra label="💡 AI Tip" value={data.ai_tip} />
            <Extra label="✍️ Prompt of the day" value={data.prompt_of_the_day} />
            <Extra label="⚙️ Automation idea" value={data.automation_idea} />
            <Extra label="📚 Learning resource" value={data.learning_resource} />
            <Extra label="🆓 Free AI tool" value={data.free_ai_tool} />
            <Extra label="📺 YouTube recommendation" value={data.youtube_recommendation} />
            <Extra label="⏱️ Productivity tip" value={data.productivity_tip} />
          </section>
        </>
      )}
    </div>
  );
}

function Extra({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <p style={{ fontFamily: "var(--font-bangla)" }}>
      <span className="font-medium" style={{ fontFamily: "var(--font-sans)" }}>
        {label}:
      </span>{" "}
      {value}
    </p>
  );
}
