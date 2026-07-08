import Link from "next/link"

import type { InterviewListItem } from "@/lib/api/interviews"
import {
  SENTIMENT_BADGE_CLASS,
  STATUS_BADGE_VARIANT,
  categoryLabel,
  formatDate,
  sentimentLabel,
} from "@/lib/taxonomy"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

export function InterviewCard({ interview }: { interview: InterviewListItem }) {
  return (
    <Link href={`/interviews/${interview.id}`} className="block h-full">
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
          <div className="min-w-0">
            <p className="truncate font-semibold leading-tight">{interview.title}</p>
            <p className="text-xs text-muted-foreground">{formatDate(interview.created_at)}</p>
          </div>
          <Badge variant={STATUS_BADGE_VARIANT[interview.status] ?? "outline"} className="shrink-0">
            {interview.status}
          </Badge>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <p className="line-clamp-2 text-sm text-muted-foreground">
            {interview.summary_preview ?? "Processing - insights aren't available yet."}
          </p>
          <div className="flex flex-wrap items-center gap-1.5">
            {interview.sentiment && (
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  SENTIMENT_BADGE_CLASS[interview.sentiment] ?? ""
                }`}
              >
                {sentimentLabel(interview.sentiment)}
              </span>
            )}
            {interview.customer_type && (
              <Badge variant="outline" className="capitalize">
                {interview.customer_type}
              </Badge>
            )}
            {interview.pain_point_categories.map((category) => (
              <Badge key={category} variant="secondary">
                {categoryLabel(category)}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
