const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export interface SemanticSearchResult {
  interview_id: string
  title: string
  summary: string | null
  similarity: number
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

export async function semanticSearch(
  query: string,
  limit = 10
): Promise<SemanticSearchResult[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/semantic-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit }),
  })
  const data = await parseOrThrow<{ results: SemanticSearchResult[] }>(
    response,
    "Semantic search"
  )
  return data.results
}
