"use client"

import { useState } from "react"

import { useInterviewsList } from "@/hooks/use-interviews-list"
import type { InterviewListFilters } from "@/lib/api/interviews"
import { EMPTY_FILTERS, type InterviewFiltersValues } from "@/lib/schemas/interview-filters"
import { ExportCsvButton } from "@/components/export/export-csv-button"
import { InterviewCard } from "@/components/interviews/interview-card"
import { InterviewFilters } from "@/components/interviews/interview-filters"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

const PAGE_SIZE = 12

function toApiFilters(values: InterviewFiltersValues): InterviewListFilters {
  return {
    q: values.q || undefined,
    status: values.status,
    sentiment: values.sentiment,
    pain_point_category: values.pain_point_category,
    customer_type: values.customer_type || undefined,
    date_from: values.date_from || undefined,
    date_to: values.date_to || undefined,
  }
}

export default function InterviewsPage() {
  const [filters, setFilters] = useState<InterviewListFilters>({})
  const [page, setPage] = useState(1)

  const queryFilters: InterviewListFilters = { ...filters, page, page_size: PAGE_SIZE }
  const { data, isLoading, isError, error, refetch, isPlaceholderData } =
    useInterviewsList(queryFilters)

  function handleApply(values: InterviewFiltersValues) {
    setFilters(toApiFilters(values))
    setPage(1)
  }

  function handleReset() {
    setFilters({})
    setPage(1)
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Interview Explorer</h1>
          <p className="text-muted-foreground">
            Browse, search, and filter every analyzed interview
          </p>
        </div>
        <ExportCsvButton filters={filters} />
      </div>

      <InterviewFilters
        defaultValues={EMPTY_FILTERS}
        onApply={handleApply}
        onReset={handleReset}
      />

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-40" />
          ))}
        </div>
      ) : isError || !data ? (
        <div className="flex flex-col items-center gap-3 py-24 text-center">
          <p className="text-sm text-muted-foreground">
            {error instanceof Error ? error.message : "Could not load interviews."}
          </p>
          <Button variant="outline" onClick={() => refetch()}>
            Try again
          </Button>
        </div>
      ) : data.items.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-24 text-center">
          <p className="text-sm text-muted-foreground">No interviews match your filters.</p>
        </div>
      ) : (
        <>
          <div
            className={`grid gap-4 sm:grid-cols-2 lg:grid-cols-3 ${
              isPlaceholderData ? "opacity-60" : ""
            }`}
          >
            {data.items.map((item) => (
              <InterviewCard key={item.id} interview={item} />
            ))}
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Page {data.page} of {data.total_pages} &middot; {data.total} total
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                disabled={page >= data.total_pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
