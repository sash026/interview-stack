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

import type { PainPointTrendPoint } from "@/lib/api/trends"
import { CATEGORY_COLOR, categoryLabel, formatDate } from "@/lib/taxonomy"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function PainPointTrendChart({ data }: { data: PainPointTrendPoint[] }) {
  const { rows, categories } = pivot(data)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pain Point Trend</CardTitle>
        <CardDescription>Which categories customers raised, over time</CardDescription>
      </CardHeader>
      <CardContent>
        {rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No pain points reported in this window.
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
                  formatter={(value, name) => [value, categoryLabel(String(name))]}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {categories.map((category) => (
                  <Bar
                    key={category}
                    dataKey={category}
                    stackId="pain-points"
                    fill={CATEGORY_COLOR[category] ?? "#94a3b8"}
                    name={categoryLabel(category)}
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

function pivot(data: PainPointTrendPoint[]) {
  const byDate = new Map<string, Record<string, number>>()
  for (const point of data) {
    const entry = byDate.get(point.date) ?? {}
    entry[point.category] = point.count
    byDate.set(point.date, entry)
  }
  const categories = Array.from(new Set(data.map((point) => point.category)))
  const rows = Array.from(byDate.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, counts]) => ({ date, ...counts }))
  return { rows, categories }
}
