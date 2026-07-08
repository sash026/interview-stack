import { z } from "zod"

export const semanticSearchSchema = z.object({
  query: z
    .string()
    .trim()
    .min(2, "Enter at least 2 characters")
    .max(500, "Query must be under 500 characters"),
})

export type SemanticSearchValues = z.infer<typeof semanticSearchSchema>
