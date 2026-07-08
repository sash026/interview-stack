import { z } from "zod"

import { PAIN_POINT_CATEGORIES, SENTIMENTS } from "@/lib/api/interviews"

export const interviewFiltersSchema = z.object({
  q: z.string().optional(),
  status: z.enum(["uploaded", "processing", "completed", "failed"]).optional(),
  sentiment: z.enum(SENTIMENTS).optional(),
  pain_point_category: z.enum(PAIN_POINT_CATEGORIES).optional(),
  customer_type: z.string().optional(),
  date_from: z.string().optional(),
  date_to: z.string().optional(),
})

export type InterviewFiltersValues = z.infer<typeof interviewFiltersSchema>

export const EMPTY_FILTERS: InterviewFiltersValues = {
  q: "",
  status: undefined,
  sentiment: undefined,
  pain_point_category: undefined,
  customer_type: "",
  date_from: "",
  date_to: "",
}
