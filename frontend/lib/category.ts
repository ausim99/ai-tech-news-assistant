export const CATEGORY_EMOJI: Record<string, string> = {
  "AI Research": "🔬",
  "AI Product": "🤖",
  "Tech Industry": "🏢",
  "Open Source": "🧩",
  Hardware: "💻",
  Policy: "⚖️",
  Other: "📰",
};

export function categoryEmoji(category: string): string {
  return CATEGORY_EMOJI[category] ?? "📰";
}
