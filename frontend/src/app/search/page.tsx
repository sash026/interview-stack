"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { Search as SearchIcon } from "lucide-react"
import { useForm } from "react-hook-form"

import { useSemanticSearch } from "@/hooks/use-semantic-search"
import { semanticSearchSchema, type SemanticSearchValues } from "@/lib/schemas/semantic-search"
import { SearchResultCard } from "@/components/interviews/search-result-card"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"

const RESULT_LIMIT = 10

export default function SearchPage() {
  const form = useForm<SemanticSearchValues>({
    resolver: zodResolver(semanticSearchSchema),
    defaultValues: { query: "" },
  })
  const searchMutation = useSemanticSearch()

  function onSubmit(values: SemanticSearchValues) {
    searchMutation.mutate({ query: values.query, limit: RESULT_LIMIT })
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Semantic Search</h1>
        <p className="text-muted-foreground">Search interviews by meaning, not just keywords</p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="flex items-start gap-3">
          <FormField
            control={form.control}
            name="query"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormControl>
                  <Input
                    placeholder="e.g. customers frustrated with pricing changes"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" disabled={searchMutation.isPending}>
            <SearchIcon className="h-4 w-4" />
            {searchMutation.isPending ? "Searching..." : "Search"}
          </Button>
        </form>
      </Form>

      {searchMutation.isPending ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <Skeleton key={index} className="h-16" />
          ))}
        </div>
      ) : searchMutation.isError ? (
        <p className="text-sm text-destructive">
          {searchMutation.error instanceof Error
            ? searchMutation.error.message
            : "Search failed. Please try again."}
        </p>
      ) : searchMutation.isSuccess ? (
        searchMutation.data.length === 0 ? (
          <Card>
            <CardContent className="py-10 text-center text-sm text-muted-foreground">
              No interviews matched that search.
            </CardContent>
          </Card>
        ) : (
          <div className="flex flex-col gap-3">
            {searchMutation.data.map((result) => (
              <SearchResultCard key={result.interview_id} result={result} />
            ))}
          </div>
        )
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-16 text-center text-sm text-muted-foreground">
            <SearchIcon className="h-6 w-6" />
            Search across every analyzed interview using natural language.
          </CardContent>
        </Card>
      )}
    </div>
  )
}
