import { z } from "zod"

const ACCEPTED_AUDIO_EXTENSIONS = [".mp3", ".wav", ".m4a"]
const MAX_AUDIO_FILE_SIZE_BYTES = 200 * 1024 * 1024 // 200MB

export const interviewUploadSchema = z
  .object({
    title: z
      .string()
      .trim()
      .min(1, "Interview name is required")
      .max(200, "Interview name must be under 200 characters"),
    audioFile: z
      .instanceof(File)
      .optional()
      .refine(
        (file) =>
          !file ||
          ACCEPTED_AUDIO_EXTENSIONS.some((ext) =>
            file.name.toLowerCase().endsWith(ext)
          ),
        `Only ${ACCEPTED_AUDIO_EXTENSIONS.join(", ")} audio files are supported`
      )
      .refine(
        (file) => !file || file.size <= MAX_AUDIO_FILE_SIZE_BYTES,
        "Audio file must be under 200MB"
      ),
    notes: z.string().trim().optional(),
  })
  .superRefine((data, ctx) => {
    const hasAudio = !!data.audioFile
    const hasNotes = !!data.notes && data.notes.length > 0

    if (!hasAudio && !hasNotes) {
      ctx.addIssue({
        code: "custom",
        message: "Provide either an audio file or text notes",
        path: ["notes"],
      })
    }

    if (hasAudio && hasNotes) {
      ctx.addIssue({
        code: "custom",
        message: "Provide only one: an audio file or text notes, not both",
        path: ["notes"],
      })
    }
  })

export type InterviewUploadValues = z.infer<typeof interviewUploadSchema>
