"use client"

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

import type { SentimentCount } from "@/lib/api/dashboard"
import { SENTIMENT_HEX, sentimentLabel } from "@/lib/taxonomy"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function SentimentChart({ data }: { data: SentimentCount[] }) {
  const total = data.reduce((sum, d) => sum + d.count, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Customer Sentiment</CardTitle>
        <CardDescription>Overall sentiment across analyzed interviews</CardDescription>
      </CardHeader>
      <CardContent>
        {total === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No sentiment data yet.
          </p>
        ) : (
          <>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data}
                    dataKey="count"
                    nameKey="sentiment"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={2}
                  >
                    {data.map((entry) => (
                      <Cell
                        key={entry.sentiment}
                        fill={SENTIMENT_HEX[entry.sentiment] ?? "#94a3b8"}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value} interviews`, ""]}
                    labelFormatter={(label) => sentimentLabel(String(label))}
                    contentStyle={{ fontSize: 12, borderRadius: 8 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {data.map((d) => (
                <div key={d.sentiment} className="flex items-center gap-2 text-sm">
                  <span
                    className="h-2 w-2 shrink-0 rounded-full"
                    style={{ backgroundColor: SENTIMENT_HEX[d.sentiment] ?? "#94a3b8" }}
                  />
                  <span className="text-muted-foreground">{sentimentLabel(d.sentiment)}</span>
                  <span className="ml-auto font-medium">{d.percentage}%</span>
                </div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
