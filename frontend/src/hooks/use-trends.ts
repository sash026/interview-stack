import { useQuery } from "@tanstack/react-query"

import { getTrends } from "@/lib/api/trends"

export function useTrends(days: number) {
  return useQuery({
    queryKey: ["trends", days],
    queryFn: () => getTrends(days),
  })
}
