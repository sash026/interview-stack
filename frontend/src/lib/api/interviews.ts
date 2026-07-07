const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export type InterviewStatusValue =
  | "uploaded"
  | "processing"
  | "completed"
  | "failed"

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

export interface InterviewDetail {
  id: string
  title: string
  status: InterviewStatusValue
  input_type: "audio" | "notes"
  failure_reason: string | null
  transcript: Transcript | null
  created_at: string
  updated_at: string
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
