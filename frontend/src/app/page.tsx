"use client"

import { FileText, MessageSquareWarning, Users } from "lucide-react"

import { useDashboardMetrics } from "@/hooks/use-dashboard-metrics"
import { categoryLabel, sentimentLabel } from "@/lib/taxonomy"
import { CompetitorList } from "@/components/dashboard/competitor-list"
import { MetricCard } from "@/components/dashboard/metric-card"
import { PainPointChart } from "@/components/dashboard/pain-point-chart"
import { RecentInterviews } from "@/components/dashboard/recent-interviews"
import { SentimentChart } from "@/components/dashboard/sentiment-chart"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

export default function DashboardPage() {
  const { data, isLoading, isError, error, refetch } = useDashboardMetrics()

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-9 w-64" />
        <div className="grid gap-4 sm:grid-cols-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-96" />
          <Skeleton className="h-96" />
        </div>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 py-24 text-center">
        <MessageSquareWarning className="h-8 w-8 text-destructive" />
        <p className="max-w-sm text-sm text-muted-foreground">
          {error instanceof Error ? error.message : "Could not load dashboard metrics."}
        </p>
        <Button variant="outline" onClick={() => refetch()}>
          Try again
        </Button>
      </div>
    )
  }

  const topPainPoint = data.top_pain_points[0]
  const topSentiment = [...data.sentiment_breakdown].sort((a, b) => b.count - a.count)[0]

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          {data.total_interviews} customer interview{data.total_interviews === 1 ? "" : "s"}{" "}
          analyzed
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Total Interviews"
          value={data.total_interviews}
          description="Fully analyzed and searchable"
          icon={<Users className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          label="Top Pain Point"
          value={topPainPoint ? categoryLabel(topPainPoint.category) : "—"}
          description={topPainPoint ? `${topPainPoint.count} mentions` : "No data yet"}
          icon={<FileText className="h-4 w-4 text-muted-foreground" />}
        />
        <MetricCard
          label="Dominant Sentiment"
          value={topSentiment ? sentimentLabel(topSentiment.sentiment) : "—"}
          description={topSentiment ? `${topSentiment.percentage}% of interviews` : "No data yet"}
          icon={<MessageSquareWarning className="h-4 w-4 text-muted-foreground" />}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <PainPointChart data={data.top_pain_points} />
        <SentimentChart data={data.sentiment_breakdown} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <CompetitorList data={data.top_competitors} />
        <RecentInterviews data={data.recent_interviews} />
      </div>
    </div>
  )
}
