"use client"

import type { ReactNode } from "react"
import Link from "next/link"
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  Clock,
  FileText,
  Lightbulb,
  ListChecks,
  Loader2,
  Mic,
  Quote,
  Sparkles,
  Swords,
  XCircle,
} from "lucide-react"

import { useInterview, useRetryInterview } from "@/hooks/use-interview"
import { useSimilarInterviews } from "@/hooks/use-similar-interviews"
import type { Insight, InterviewDetail } from "@/lib/api/interviews"
import {
  SENTIMENT_BADGE_CLASS,
  STATUS_BADGE_VARIANT,
  categoryLabel,
  formatDate,
  sentimentLabel,
} from "@/lib/taxonomy"
import { SearchResultCard } from "@/components/interviews/search-result-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function InterviewDetailView({ interviewId }: { interviewId: string }) {
  const { data: interview, isLoading, isError, error } = useInterview(interviewId)
  const retryMutation = useRetryInterview(interviewId)

  if (isLoading) {
    return <DetailSkeleton />
  }

  if (isError || !interview) {
    return (
      <div className="flex flex-col gap-4">
        <BackLink />
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            {error instanceof Error ? error.message : "Could not load this interview."}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <BackLink />

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight">{interview.title}</h1>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              {interview.input_type === "audio" ? (
                <Mic className="h-3.5 w-3.5" />
              ) : (
                <FileText className="h-3.5 w-3.5" />
              )}
              {interview.input_type === "audio" ? "Audio" : "Notes"}
            </span>
            <span aria-hidden>&middot;</span>
            <span>{formatDate(interview.created_at)}</span>
          </div>
        </div>
        <Badge variant={STATUS_BADGE_VARIANT[interview.status] ?? "outline"} className="capitalize">
          {interview.status}
        </Badge>
      </div>

      {interview.status !== "completed" ? (
        <InFlightCard
          interview={interview}
          onRetry={() => retryMutation.mutate()}
          isRetrying={retryMutation.isPending}
          retryError={retryMutation.error}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="flex flex-col gap-6 lg:col-span-2">
            <Tabs defaultValue="overview">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="transcript">Transcript</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="flex flex-col gap-6 pt-4">
                {interview.insights && <InsightsSections insights={interview.insights} />}
              </TabsContent>
              <TabsContent value="transcript" className="pt-4">
                <TranscriptViewer text={interview.transcript?.raw_text ?? null} />
              </TabsContent>
            </Tabs>
          </div>

          <div className="flex flex-col gap-6">
            {interview.insights && <MetadataCard insights={interview.insights} />}
            <SimilarInterviews interviewId={interview.id} />
          </div>
        </div>
      )}
    </div>
  )
}

function BackLink() {
  return (
    <Link
      href="/interviews"
      className="inline-flex w-fit items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
    >
      <ArrowLeft className="h-3.5 w-3.5" />
      Back to Explorer
    </Link>
  )
}

function InFlightCard({
  interview,
  onRetry,
  isRetrying,
  retryError,
}: {
  interview: InterviewDetail
  onRetry: () => void
  isRetrying: boolean
  retryError: unknown
}) {
  if (interview.status === "failed") {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
          <XCircle className="h-8 w-8 text-destructive" />
          <p className="text-sm font-medium">Processing failed</p>
          {interview.failure_reason && (
            <p className="max-w-md text-sm text-muted-foreground">{interview.failure_reason}</p>
          )}
          {retryError instanceof Error && (
            <p className="text-sm text-destructive">{retryError.message}</p>
          )}
          <Button variant="outline" onClick={onRetry} disabled={isRetrying}>
            {isRetrying ? "Retrying..." : "Retry processing"}
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-3 py-10 text-center">
        {interview.status === "uploaded" ? (
          <Clock className="h-8 w-8 text-muted-foreground" />
        ) : (
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        )}
        <p className="text-sm font-medium">
          {interview.status === "uploaded" ? "Queued for processing" : "Transcribing and analyzing..."}
        </p>
        <p className="max-w-md text-sm text-muted-foreground">
          This page updates automatically once insights are ready.
        </p>
      </CardContent>
    </Card>
  )
}

function InsightsSections({ insights }: { insights: Insight }) {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed">{insights.summary}</p>
        </CardContent>
      </Card>

      {insights.pain_points.length > 0 && (
        <Section icon={<AlertTriangle className="h-4 w-4" />} title="Pain Points">
          <div className="flex flex-col gap-3">
            {insights.pain_points.map((point, index) => (
              <div key={index} className="flex flex-col gap-1">
                <Badge variant="secondary" className="w-fit">
                  {categoryLabel(point.category)}
                </Badge>
                <p className="text-sm text-muted-foreground">{point.description}</p>
              </div>
            ))}
          </div>
        </Section>
      )}

      {insights.feature_requests.length > 0 && (
        <Section icon={<Lightbulb className="h-4 w-4" />} title="Feature Requests">
          <ul className="flex flex-col gap-1.5 text-sm">
            {insights.feature_requests.map((item, index) => (
              <li key={index} className="flex gap-2">
                <span className="text-muted-foreground" aria-hidden>
                  &bull;
                </span>
                {item}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {insights.competitors.length > 0 && (
        <Section icon={<Swords className="h-4 w-4" />} title="Competitors Mentioned">
          <div className="flex flex-wrap gap-1.5">
            {insights.competitors.map((competitor) => (
              <Badge key={competitor} variant="outline">
                {competitor}
              </Badge>
            ))}
          </div>
        </Section>
      )}

      {insights.notable_quotes.length > 0 && (
        <Section icon={<Quote className="h-4 w-4" />} title="Notable Quotes">
          <div className="flex flex-col gap-3">
            {insights.notable_quotes.map((quote, index) => (
              <blockquote
                key={index}
                className="border-l-2 border-border pl-3 text-sm italic text-muted-foreground"
              >
                &ldquo;{quote}&rdquo;
              </blockquote>
            ))}
          </div>
        </Section>
      )}

      {insights.action_items.length > 0 && (
        <Section icon={<ListChecks className="h-4 w-4" />} title="Action Items">
          <ul className="flex flex-col gap-1.5 text-sm">
            {insights.action_items.map((item, index) => (
              <li key={index} className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                {item}
              </li>
            ))}
          </ul>
        </Section>
      )}
    </>
  )
}

function Section({
  icon,
  title,
  children,
}: {
  icon: ReactNode
  title: string
  children: ReactNode
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

function TranscriptViewer({ text }: { text: string | null }) {
  return (
    <Card>
      <CardContent className="max-h-[32rem] overflow-y-auto text-sm leading-relaxed whitespace-pre-wrap">
        {text ?? "No transcript text available."}
      </CardContent>
    </Card>
  )
}

function MetadataCard({ insights }: { insights: Insight }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Details</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 text-sm">
        <MetaRow label="Sentiment">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${
              SENTIMENT_BADGE_CLASS[insights.customer_sentiment] ?? ""
            }`}
          >
            {sentimentLabel(insights.customer_sentiment)}
          </span>
        </MetaRow>
        <Separator />
        <MetaRow label="Customer type">
          <span className="capitalize">{insights.customer_type}</span>
        </MetaRow>
      </CardContent>
    </Card>
  )
}

function MetaRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      {children}
    </div>
  )
}

function SimilarInterviews({ interviewId }: { interviewId: string }) {
  const { data, isLoading, isError } = useSimilarInterviews(interviewId, 5)

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="h-4 w-4" />
            Similar Interviews
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-12" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (isError || !data || data.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="h-4 w-4" />
          Similar Interviews
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {data.map((result) => (
          <SearchResultCard key={result.interview_id} result={result} />
        ))}
      </CardContent>
    </Card>
  )
}

function DetailSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-8 w-64" />
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Skeleton className="h-40" />
          <Skeleton className="h-40" />
        </div>
        <Skeleton className="h-40" />
      </div>
    </div>
  )
}
