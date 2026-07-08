import Link from "next/link"

import type { RecentInterviewItem } from "@/lib/api/dashboard"
import {
  SENTIMENT_BADGE_CLASS,
  STATUS_BADGE_VARIANT,
  formatDate,
  sentimentLabel,
} from "@/lib/taxonomy"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function RecentInterviews({ data }: { data: RecentInterviewItem[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Interviews</CardTitle>
        <CardDescription>Latest uploads, most recent first</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col divide-y">
        {data.length === 0 ? (
          <p className="py-4 text-sm text-muted-foreground">
            No interviews yet. Upload your first one to get started.
          </p>
        ) : (
          data.map((item) => (
            <Link
              key={item.id}
              href={`/interviews/${item.id}`}
              className="-mx-2 flex flex-col gap-1 rounded-md px-2 py-3 transition-colors first:pt-0 last:pb-0 hover:bg-muted/40"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium">{item.title}</span>
                <div className="flex shrink-0 items-center gap-2">
                  {item.sentiment && (
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        SENTIMENT_BADGE_CLASS[item.sentiment] ?? ""
                      }`}
                    >
                      {sentimentLabel(item.sentiment)}
                    </span>
                  )}
                  <Badge variant={STATUS_BADGE_VARIANT[item.status] ?? "outline"}>
                    {item.status}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between gap-2 text-sm text-muted-foreground">
                <span className="line-clamp-1">
                  {item.summary_preview ?? "Processing..."}
                </span>
                <span className="shrink-0">{formatDate(item.created_at)}</span>
              </div>
            </Link>
          ))
        )}
      </CardContent>
    </Card>
  )
}
