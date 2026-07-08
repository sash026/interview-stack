"use client"

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import type { CategoryBreakdownItem } from "@/lib/api/trends"
import { CATEGORY_COLOR, categoryLabel } from "@/lib/taxonomy"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function CategoryBreakdownChart({ data }: { data: CategoryBreakdownItem[] }) {
  const chartData = data.map((d) => ({
    category: d.category,
    label: categoryLabel(d.category),
    count: d.count,
  }))

  return (
    <Card>
      <CardHeader>
        <CardTitle>Category Breakdown</CardTitle>
        <CardDescription>All pain point categories mentioned in this window</CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No pain points extracted in this window.
          </p>
        ) : (
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="label" width={110} tick={{ fontSize: 12 }} />
                <Tooltip
                  cursor={{ fill: "var(--muted)" }}
                  contentStyle={{ fontSize: 12, borderRadius: 8 }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Mentions">
                  {chartData.map((entry) => (
                    <Cell key={entry.category} fill={CATEGORY_COLOR[entry.category] ?? "#94a3b8"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
