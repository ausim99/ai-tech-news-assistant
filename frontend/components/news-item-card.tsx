"use client";

import { useState } from "react";
import type { NewsItem } from "@/lib/types";
import { categoryEmoji } from "@/lib/category";

export function NewsItemCard({ item }: { item: NewsItem }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <article className="rounded-lg border border-border bg-card p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium leading-snug" style={{ fontFamily: "var(--font-bangla)" }}>
          {categoryEmoji(item.category)} {item.title_bn || item.title}
        </h3>
        <span className="shrink-0 text-xs text-muted rounded-full border border-border px-2 py-0.5">
          {item.category || "Other"}
        </span>
      </div>

      <p className="text-xs text-muted">
        {item.source} {item.confidence != null && `· confidence ${Math.round(item.confidence * 100)}%`}
      </p>

      <p className="text-sm" style={{ fontFamily: "var(--font-bangla)" }}>
        {item.summary_bn || item.summary}
      </p>

      {item.why_it_matters_bn && (
        <p className="text-sm text-muted" style={{ fontFamily: "var(--font-bangla)" }}>
          <span className="font-medium text-foreground">কেন গুরুত্বপূর্ণ:</span> {item.why_it_matters_bn}
        </p>
      )}

      <div className="flex items-center gap-3 pt-1">
        <a
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-accent hover:underline"
        >
          আরও পড়ুন →
        </a>
        {item.tutorial && (
          <button
            onClick={() => setExpanded((e) => !e)}
            className="text-sm text-muted hover:text-foreground"
          >
            {expanded ? "Hide tutorial ▲" : "Show tutorial ▼"}
          </button>
        )}
      </div>

      {expanded && item.tutorial && <TutorialPanel tutorial={item.tutorial} />}
    </article>
  );
}

function TutorialPanel({ tutorial }: { tutorial: NonNullable<NewsItem["tutorial"]> }) {
  return (
    <div className="mt-2 rounded-md border border-border bg-background p-3 space-y-2 text-sm">
      <Field label="What happened" value={tutorial.what_happened} />
      <Field label="Why it matters" value={tutorial.why_it_matters} />
      <Field label="Who should care" value={tutorial.who_should_care} />
      <Field label="Real-world example" value={tutorial.real_world_example} />
      <ListField label="Steps" items={tutorial.steps} ordered />
      <ListField label="Advantages" items={tutorial.advantages} />
      <ListField label="Disadvantages" items={tutorial.disadvantages} />
      <Field label="Future impact" value={tutorial.future_impact} />
      <ListField label="Learning resources" items={tutorial.learning_resources} />
      <ListField label="GitHub repos" items={tutorial.github_repos} />
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <p>
      <span className="font-medium">{label}:</span> {value}
    </p>
  );
}

function ListField({ label, items, ordered }: { label: string; items: string[]; ordered?: boolean }) {
  if (!items?.length) return null;
  const List = ordered ? "ol" : "ul";
  return (
    <div>
      <span className="font-medium">{label}:</span>
      <List className={ordered ? "list-decimal pl-5 mt-1 space-y-0.5" : "list-disc pl-5 mt-1 space-y-0.5"}>
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </List>
    </div>
  );
}
