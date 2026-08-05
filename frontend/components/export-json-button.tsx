"use client";

export function ExportJsonButton({ data, filename }: { data: unknown; filename: string }) {
  function handleExport() {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button
      onClick={handleExport}
      className="rounded-md border border-border px-3 py-1.5 text-sm hover:bg-card transition-colors"
    >
      ⬇ Export JSON
    </button>
  );
}
