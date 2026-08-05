export default function AboutPage() {
  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-xl font-semibold">About</h1>

      <div className="rounded-lg border border-border bg-card p-4 space-y-3 text-sm leading-relaxed">
        <p>
          AI Tech News Assistant collects AI and technology news daily from ~20 curated sources,
          researches and fact-checks each story with an LLM, translates it into natural Bangla, adds a
          practical tutorial for the most important stories, and delivers a ranked digest to Telegram and
          WhatsApp every morning at 06:00 (Asia/Dhaka).
        </p>
        <p>This dashboard reads data straight from the GitHub repo - no separate database, no redeploy needed to see fresh data.</p>
      </div>

      <div className="rounded-lg border border-border bg-card p-4 space-y-2 text-sm">
        <h2 className="font-medium">Stack</h2>
        <ul className="list-disc pl-5 space-y-0.5 text-muted">
          <li>Python 3.13, FastAPI, httpx, Loguru, uv</li>
          <li>xAI Grok for research/translation/tutorial/digest generation</li>
          <li>GitHub Actions for the daily pipeline, healthcheck, and cleanup</li>
          <li>Next.js, TypeScript, Tailwind CSS - this dashboard</li>
          <li>Vercel for both the API and the dashboard</li>
        </ul>
      </div>
    </div>
  );
}
