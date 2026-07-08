const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface PainPointCount {
  category: string
  count: number
}

export interface CompetitorCount {
  name: string
  count: number
}

export interface SentimentCount {
  sentiment: string
  count: number
  percentage: number
}

export interface RecentInterviewItem {
  id: string
  title: string
  status: string
  created_at: string
  sentiment: string | null
  summary_preview: string | null
}

export interface DashboardMetrics {
  total_interviews: number
  top_pain_points: PainPointCount[]
  sentiment_breakdown: SentimentCount[]
  top_competitors: CompetitorCount[]
  recent_interviews: RecentInterviewItem[]
}

async function parseOrThrow<T>(response: Response, action: string): Promise<T> {
  if (!response.ok) {
    const errorBody = await response.text()
    throw new Error(
      `${action} failed (${response.status}): ${errorBody || response.statusText}`
    )
  }
  return response.json()
}

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/metrics`)
  return parseOrThrow(response, "Fetching dashboard metrics")
}
