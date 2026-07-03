const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

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

  const response = await fetch(
    `${API_BASE_URL}/api/v1/interviews/upload`,
    {
      method: "POST",
      body: formData,
    }
  )

  if (!response.ok) {
    const errorBody = await response.text()
    throw new Error(
      `Upload failed (${response.status}): ${errorBody || response.statusText}`
    )
  }

  return response.json()
}
