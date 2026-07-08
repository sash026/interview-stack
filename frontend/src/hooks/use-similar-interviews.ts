import { useQuery } from "@tanstack/react-query"

import { getSimilarInterviews } from "@/lib/api/interviews"

export function useSimilarInterviews(interviewId: string | null, limit = 5) {
  return useQuery({
    queryKey: ["similar-interviews", interviewId, limit],
    queryFn: () => getSimilarInterviews(interviewId as string, limit),
    enabled: interviewId !== null,
    retry: false,
  })
}
