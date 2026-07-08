"use client"

import { useState } from "react"
import { MessageSquareWarning } from "lucide-react"

import { useTrends } from "@/hooks/use-trends"
import { CategoryBreakdownChart } from "@/components/trends/category-breakdown-chart"
import { PainPointTrendChart } from "@/components/trends/pain-point-trend-chart"
import { SentimentTrendChart } from "@/components/trends/sentiment-trend-chart"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"

const DAY_RANGE_OPTIONS = [
  { value: "7", label: "Last 7 days" },
  { value: "30", label: "Last 30 days" },
  { value: "90", label: "Last 90 days" },
]

export default function TrendsPage() {
  const [days, setDays] = useState(30)
  const { data, isLoading, isError, error, refetch } = useTrends(days)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Trends</h1>
          <p className="text-muted-foreground">
            How pain points and sentiment have shifted over time
          </p>
        </div>
        <Select value={String(days)} onValueChange={(value) => setDays(Number(value))}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {DAY_RANGE_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
          <Skeleton className="h-96 lg:col-span-2" />
        </div>
      ) : isError || !data ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 py-24 text-center">
          <MessageSquareWarning className="h-8 w-8 text-destructive" />
          <p className="max-w-sm text-sm text-muted-foreground">
            {error instanceof Error ? error.message : "Could not load trends."}
          </p>
          <Button variant="outline" onClick={() => refetch()}>
            Try again
          </Button>
        </div>
      ) : (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <PainPointTrendChart data={data.pain_point_trends} />
            <SentimentTrendChart data={data.sentiment_trends} />
          </div>
          <CategoryBreakdownChart data={data.category_breakdown} />
        </>
      )}
    </div>
  )
}
