import Link from "next/link"

import type { SemanticSearchResult } from "@/lib/api/search"
import { Badge } from "@/components/ui/badge"

export function SearchResultCard({ result }: { result: SemanticSearchResult }) {
  return (
    <Link
      href={`/interviews/${result.interview_id}`}
      className="flex flex-col gap-1 rounded-lg border p-3 transition-colors hover:bg-muted/50"
    >
      <div className="flex items-center justify-between gap-2">
        <p className="truncate text-sm font-medium">{result.title}</p>
        <Badge variant="outline" className="shrink-0 text-xs">
          {Math.round(result.similarity * 100)}%
        </Badge>
      </div>
      {result.summary && (
        <p className="line-clamp-2 text-xs text-muted-foreground">{result.summary}</p>
      )}
    </Link>
  )
}
