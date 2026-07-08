import type { SemanticSearchResult } from "@/lib/api/search"

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export type InterviewStatusValue =
  | "uploaded"
  | "processing"
  | "completed"
  | "failed"

export type InputTypeValue = "audio" | "notes"

export const PAIN_POINT_CATEGORIES = [
  "pricing",
  "reporting",
  "authentication",
  "onboarding",
  "integrations",
  "performance",
  "ux",
  "documentation",
  "analytics",
  "security",
  "collaboration",
  "support",
] as const

export type PainPointCategory = (typeof PAIN_POINT_CATEGORIES)[number]

export const SENTIMENTS = ["positive", "neutral", "negative", "mixed"] as const
export type Sentiment = (typeof SENTIMENTS)[number]

export interface UploadInterviewInput {
  title: string
  audioFile?: File
  notes?: string
}

export interface UploadInterviewResponse {
  id: string
  title: string
  status: string
  has_audio: boolean
  has_notes: boolean
}

export interface InterviewStatusResponse {
  id: string
  status: InterviewStatusValue
  failure_reason: string | null
}

export interface Transcript {
  raw_text: string | null
  created_at: string
  updated_at: string
}

export interface PainPoint {
  category: string
  description: string
}

export interface Insight {
  summary: string
  pain_points: PainPoint[]
  feature_requests: string[]
  competitors: string[]
  customer_sentiment: string
  customer_type: string
  action_items: string[]
  notable_quotes: string[]
  created_at: string
  updated_at: string
}

export interface InterviewDetail {
  id: string
  title: string
  status: InterviewStatusValue
  input_type: InputTypeValue
  failure_reason: string | null
  transcript: Transcript | null
  insights: Insight | null
  created_at: string
  updated_at: string
}

export interface InterviewListItem {
  id: string
  title: string
  status: InterviewStatusValue
  input_type: InputTypeValue
  created_at: string
  sentiment: string | null
  customer_type: string | null
  summary_preview: string | null
  pain_point_categories: string[]
  competitors: string[]
}

export interface InterviewListResponse {
  items: InterviewListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface InterviewListFilters {
  page?: number
  page_size?: number
  status?: InterviewStatusValue
  sentiment?: Sentiment
  pain_point_category?: PainPointCategory
  customer_type?: string
  date_from?: string
  date_to?: string
  q?: string
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

export async function uploadInterview(
  input: UploadInterviewInput
): Promise<UploadInterviewResponse> {
  const formData = new FormData()
  formData.append("title", input.title)
  if (input.audioFile) {
    formData.append("audio_file", input.audioFile)
  }
  if (input.notes) {
    formData.append("notes", input.notes)
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/interviews/upload`, {
    method: "POST",
    body: formData,
  })

  return parseOrThrow(response, "Upload")
}

export async function getInterview(interviewId: string): Promise<InterviewDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/interviews/${interviewId}`)
  return parseOrThrow(response, "Fetching interview")
}

export async function getInterviewStatus(
  interviewId: string
): Promise<InterviewStatusResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/interviews/${interviewId}/status`
  )
  return parseOrThrow(response, "Fetching interview status")
}

export async function retryInterview(
  interviewId: string
): Promise<InterviewStatusResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/interviews/${interviewId}/retry`,
    { method: "POST" }
  )
  return parseOrThrow(response, "Retrying interview")
}

export async function getSimilarInterviews(
  interviewId: string,
  limit = 5
): Promise<SemanticSearchResult[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/interviews/${interviewId}/similar?limit=${limit}`
  )
  const data = await parseOrThrow<{ results: SemanticSearchResult[] }>(
    response,
    "Fetching similar interviews"
  )
  return data.results
}

export async function listInterviews(
  filters: InterviewListFilters
): Promise<InterviewListResponse> {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value))
    }
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/interviews?${params.toString()}`
  )
  return parseOrThrow(response, "Fetching interviews")
}
