"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { SENTIMENTS } from "@/lib/api/interviews"
import type { SentimentTrendPoint } from "@/lib/api/trends"
import { SENTIMENT_HEX, formatDate, sentimentLabel } from "@/lib/taxonomy"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function SentimentTrendChart({ data }: { data: SentimentTrendPoint[] }) {
  const { rows, sentiments } = pivot(data)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sentiment Trend</CardTitle>
        <CardDescription>Customer sentiment across analyzed interviews, over time</CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No sentiment data in this window.
          </p>
        ) : (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rows} margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                <XAxis dataKey="date" tickFormatter={formatDate} tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip
                  labelFormatter={(value) => formatDate(String(value))}
                  formatter={(value, name) => [value, sentimentLabel(String(name))]}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {sentiments.map((sentiment) => (
                  <Bar
                    key={sentiment}
                    dataKey={sentiment}
                    stackId="sentiment"
                    fill={SENTIMENT_HEX[sentiment] ?? "#94a3b8"}
                    name={sentimentLabel(sentiment)}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function pivot(data: SentimentTrendPoint[]) {
  const byDate = new Map<string, Record<string, number>>()
  for (const point of data) {
    const entry = byDate.get(point.date) ?? {}
    entry[point.sentiment] = point.count
    byDate.set(point.date, entry)
  }
  const present = new Set(data.map((point) => point.sentiment))
  const sentiments = SENTIMENTS.filter((sentiment) => present.has(sentiment))
  const rows = Array.from(byDate.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }))
  return { rows, sentiments }
}
