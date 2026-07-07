import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  getInterview,
  retryInterview,
  type InterviewDetail,
} from "@/lib/api/interviews"

const POLL_INTERVAL_MS = 3000

const IN_FLIGHT_STATUSES = new Set(["uploaded", "processing"])

function interviewQueryKey(interviewId: string) {
  return ["interview", interviewId] as const
}

export function useInterview(interviewId: string | null) {
  return useQuery({
    queryKey: interviewId ? interviewQueryKey(interviewId) : ["interview", "none"],
    queryFn: () => getInterview(interviewId as string),
    enabled: interviewId !== null,
    refetchInterval: (query) => {
      const data = query.state.data as InterviewDetail | undefined
      if (!data || IN_FLIGHT_STATUSES.has(data.status)) {
        return POLL_INTERVAL_MS
      }
      return false
    },
  })
}

export function useRetryInterview(interviewId: string | null) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => retryInterview(interviewId as string),
    onSuccess: () => {
      if (interviewId) {
        queryClient.invalidateQueries({ queryKey: interviewQueryKey(interviewId) })
      }
    },
  })
}
