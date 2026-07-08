export const CATEGORY_LABELS: Record<string, string> = {
  pricing: "Pricing",
  reporting: "Reporting",
  authentication: "Authentication",
  onboarding: "Onboarding",
  integrations: "Integrations",
  performance: "Performance",
  ux: "UX",
  documentation: "Documentation",
  analytics: "Analytics",
  security: "Security",
  collaboration: "Collaboration",
  support: "Support",
}

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category
}

export const SENTIMENT_LABELS: Record<string, string> = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
  mixed: "Mixed",
}

export function sentimentLabel(sentiment: string): string {
  return SENTIMENT_LABELS[sentiment] ?? sentiment
}

export const SENTIMENT_HEX: Record<string, string> = {
  positive: "#16a34a",
  neutral: "#71717a",
  negative: "#dc2626",
  mixed: "#d97706",
}

export const SENTIMENT_BADGE_CLASS: Record<string, string> = {
  positive: "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  negative: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  neutral: "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-300",
  mixed: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
}

export const STATUS_BADGE_VARIANT: Record<
  string,
  "default" | "secondary" | "destructive" | "outline"
> = {
  completed: "default",
  processing: "secondary",
  uploaded: "outline",
  failed: "destructive",
}

export const CHART_PALETTE = [
  "#2563eb",
  "#16a34a",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
  "#db2777",
  "#65a30d",
  "#ea580c",
  "#4f46e5",
  "#0d9488",
  "#9333ea",
]

export const CATEGORY_COLOR: Record<string, string> = Object.fromEntries(
  Object.keys(CATEGORY_LABELS).map((category, index) => [category, CHART_PALETTE[index]])
)

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}
