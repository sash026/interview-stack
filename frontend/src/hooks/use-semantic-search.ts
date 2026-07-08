import { useMutation } from "@tanstack/react-query"

import { semanticSearch } from "@/lib/api/search"

export function useSemanticSearch() {
  return useMutation({
    mutationFn: ({ query, limit }: { query: string; limit?: number }) =>
      semanticSearch(query, limit),
  })
}
