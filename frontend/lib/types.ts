export interface Tutorial {
  what_happened: string;
  why_it_matters: string;
  who_should_care: string;
  real_world_example: string;
  steps: string[];
  advantages: string[];
  disadvantages: string[];
  future_impact: string;
  learning_resources: string[];
  github_repos: string[];
}

export interface NewsItem {
  link: string;
  title: string;
  source: string;
  author: string;
  category: string;
  summary: string;
  key_facts: string[];
  risk: string;
  future_impact: string;
  confidence: number;
  title_bn?: string;
  summary_bn?: string;
  why_it_matters_bn?: string;
  tutorial: Tutorial | null;
}

export interface Digest {
  date: string;
  generated_at: string;
  top_ai_news: NewsItem[];
  top_tech_news: NewsItem[];
  ai_tip: string;
  prompt_of_the_day: string;
  automation_idea: string;
  learning_resource: string;
  free_ai_tool: string;
  youtube_recommendation: string;
  productivity_tip: string;
  items: NewsItem[];
}

export interface HistoryEntry {
  date: string;
  top_ai_count: number;
  top_tech_count: number;
}

export interface LogEntry {
  timestamp: string;
  status: "ok" | "empty" | string;
  item_count: number;
}

export interface Analytics {
  total_runs_logged: number;
  successful_runs: number;
  success_rate: number | null;
  last_run: LogEntry | null;
  updated_at: string;
}

export interface StatusResponse {
  last_run: {
    status: string | null;
    conclusion: string | null;
    started_at: string | null;
    url: string | null;
  } | null;
  analytics: Analytics;
}

export interface WorkflowRun {
  id: number;
  status: string;
  conclusion: string | null;
  run_started_at: string;
  html_url: string;
  display_title?: string;
}

export type WorkflowsResponse = Record<string, WorkflowRun[]>;

export interface SourceConfig {
  name: string;
  rss_url: string | null;
  category: string;
  status?: string;
  note?: string;
}

export interface ConfigResponse {
  max_tutorial_items: number;
  schedule: Record<string, string>;
  sources: SourceConfig[];
}
