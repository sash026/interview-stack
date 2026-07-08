import { useQuery } from "@tanstack/react-query"

import { listInterviews, type InterviewListFilters } from "@/lib/api/interviews"

export function useInterviewsList(filters: InterviewListFilters) {
  return useQuery({
    queryKey: ["interviews", filters],
    queryFn: () => listInterviews(filters),
    placeholderData: (previousData) => previousData,
  })
}
