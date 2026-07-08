import type { CompetitorCount } from "@/lib/api/dashboard"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function CompetitorList({ data }: { data: CompetitorCount[] }) {
  const maxCount = Math.max(...data.map((d) => d.count), 1)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Competitors Mentioned</CardTitle>
        <CardDescription>How often each came up in customer conversations</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {data.length === 0 ? (
          <p className="py-4 text-sm text-muted-foreground">No competitor mentions yet.</p>
        ) : (
          data.map((competitor) => (
            <div key={competitor.name} className="flex items-center gap-3">
              <span className="w-28 shrink-0 truncate text-sm font-medium">
                {competitor.name}
              </span>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-blue-600"
                  style={{ width: `${(competitor.count / maxCount) * 100}%` }}
                />
              </div>
              <Badge variant="secondary" className="shrink-0">
                {competitor.count}
              </Badge>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
