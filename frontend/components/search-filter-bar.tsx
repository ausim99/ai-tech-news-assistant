"use client";

export function SearchFilterBar({
  search,
  onSearchChange,
  category,
  onCategoryChange,
  categories,
}: {
  search: string;
  onSearchChange: (v: string) => void;
  category: string;
  onCategoryChange: (v: string) => void;
  categories: string[];
}) {
  return (
    <div className="flex flex-col sm:flex-row gap-2">
      <input
        type="search"
        placeholder="Search headlines..."
        value={search}
        onChange={(e) => onSearchChange(e.target.value)}
        className="flex-1 rounded-md border border-border bg-card px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent"
      />
      <select
        value={category}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="rounded-md border border-border bg-card px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent"
      >
        <option value="">All categories</option>
        {categories.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
    </div>
  );
}
