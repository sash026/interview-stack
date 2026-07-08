"use client"

import { Download } from "lucide-react"
import { useState } from "react"

import { listInterviews, type InterviewListFilters } from "@/lib/api/interviews"
import { Button } from "@/components/ui/button"

const EXPORT_COLUMNS = [
  "date",
  "customer",
  "status",
  "sentiment",
  "customer_type",
  "summary",
  "pain_points",
  "competitors",
] as const

function csvEscape(value: string): string {
  if (/[",\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

function toCsv(rows: Record<(typeof EXPORT_COLUMNS)[number], string>[]): string {
  const header = EXPORT_COLUMNS.join(",")
  const body = rows
    .map((row) => EXPORT_COLUMNS.map((col) => csvEscape(row[col])).join(","))
    .join("\n")
  return `${header}\n${body}`
}

function downloadCsv(csv: string): void {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  link.download = `interviews-export-${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

export function ExportCsvButton({ filters }: { filters: InterviewListFilters }) {
  const [isExporting, setIsExporting] = useState(false)

  async function handleExport() {
    setIsExporting(true)
    try {
      const items = []
      let page = 1
      const pageSize = 100
      for (;;) {
        const response = await listInterviews({ ...filters, page, page_size: pageSize })
        items.push(...response.items)
        if (page >= response.total_pages) break
        page += 1
      }

      const rows = items.map((item) => ({
        date: new Date(item.created_at).toISOString().slice(0, 10),
        customer: item.title,
        status: item.status,
        sentiment: item.sentiment ?? "",
        customer_type: item.customer_type ?? "",
        summary: item.summary_preview ?? "",
        pain_points: item.pain_point_categories.join("; "),
        competitors: item.competitors.join("; "),
      }))

      downloadCsv(toCsv(rows))
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button variant="outline" onClick={handleExport} disabled={isExporting}>
      <Download className="h-4 w-4" />
      {isExporting ? "Exporting..." : "Export CSV"}
    </Button>
  )
}
