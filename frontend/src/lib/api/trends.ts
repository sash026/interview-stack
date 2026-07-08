const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface PainPointTrendPoint {
  date: string
  category: string
  count: number
}

export interface SentimentTrendPoint {
  date: string
  sentiment: string
  count: number
}

export interface CategoryBreakdownItem {
  category: string
  count: number
}

export interface TrendsData {
  days: number
  pain_point_trends: PainPointTrendPoint[]
  sentiment_trends: SentimentTrendPoint[]
  category_breakdown: CategoryBreakdownItem[]
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

export async function getTrends(days = 30): Promise<TrendsData> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analytics/trends?days=${days}`)
  return parseOrThrow(response, "Fetching trends")
}
