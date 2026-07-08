import { useQuery } from "@tanstack/react-query"

import { getDashboardMetrics } from "@/lib/api/dashboard"

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: getDashboardMetrics,
  })
}
