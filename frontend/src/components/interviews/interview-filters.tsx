"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"

import { PAIN_POINT_CATEGORIES, SENTIMENTS } from "@/lib/api/interviews"
import {
  EMPTY_FILTERS,
  interviewFiltersSchema,
  type InterviewFiltersValues,
} from "@/lib/schemas/interview-filters"
import { categoryLabel, sentimentLabel } from "@/lib/taxonomy"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const ALL = "all"

interface InterviewFiltersProps {
  defaultValues: InterviewFiltersValues
  onApply: (values: InterviewFiltersValues) => void
  onReset: () => void
}

export function InterviewFilters({
  defaultValues,
  onApply,
  onReset,
}: InterviewFiltersProps) {
  const { register, control, handleSubmit, reset } = useForm<InterviewFiltersValues>({
    resolver: zodResolver(interviewFiltersSchema),
    defaultValues,
  })

  function handleReset() {
    reset(EMPTY_FILTERS)
    onReset()
  }

  return (
    <form
      onSubmit={handleSubmit(onApply, (errors) =>
        console.error("Filter form validation failed:", errors),
      )}
      className="flex flex-col gap-3 rounded-lg border bg-card p-4"
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Input placeholder="Search by title..." {...register("q")} />

        <Controller
          control={control}
          name="status"
          render={({ field }) => (
            <Select
              value={field.value ?? ALL}
              onValueChange={(value) => field.onChange(value === ALL ? undefined : value)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All statuses</SelectItem>
                <SelectItem value="uploaded">Uploaded</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          )}
        />

        <Controller
          control={control}
          name="sentiment"
          render={({ field }) => (
            <Select
              value={field.value ?? ALL}
              onValueChange={(value) => field.onChange(value === ALL ? undefined : value)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Sentiment" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All sentiments</SelectItem>
                {SENTIMENTS.map((sentiment) => (
                  <SelectItem key={sentiment} value={sentiment}>
                    {sentimentLabel(sentiment)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />

        <Controller
          control={control}
          name="pain_point_category"
          render={({ field }) => (
            <Select
              value={field.value ?? ALL}
              onValueChange={(value) => field.onChange(value === ALL ? undefined : value)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Pain point category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All categories</SelectItem>
                {PAIN_POINT_CATEGORIES.map((category) => (
                  <SelectItem key={category} value={category}>
                    {categoryLabel(category)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Input placeholder="Customer type (e.g. enterprise)" {...register("customer_type")} />
        <Input type="date" aria-label="From date" {...register("date_from")} />
        <Input type="date" aria-label="To date" {...register("date_to")} />
        <div className="flex gap-2">
          <Button type="submit" className="flex-1">
            Apply Filters
          </Button>
          <Button type="button" variant="outline" onClick={handleReset}>
            Reset
          </Button>
        </div>
      </div>
    </form>
  )
}
