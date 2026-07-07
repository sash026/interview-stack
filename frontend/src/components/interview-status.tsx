"use client"

import { CheckCircle2, Clock, Loader2, XCircle } from "lucide-react"

import { useInterview, useRetryInterview } from "@/hooks/use-interview"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function InterviewStatus({ interviewId }: { interviewId: string }) {
  const { data: interview, isLoading, isError, error } = useInterview(interviewId)
  const retryMutation = useRetryInterview(interviewId)

  if (isLoading) {
    return (
      <Card className="w-full max-w-lg">
        <CardContent className="flex items-center gap-2 py-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading interview status...
        </CardContent>
      </Card>
    )
  }

  if (isError || !interview) {
    return (
      <Card className="w-full max-w-lg">
        <CardContent className="py-6 text-sm text-destructive">
          {error instanceof Error ? error.message : "Could not load interview status."}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-lg">
      <CardHeader>
        <CardTitle>{interview.title}</CardTitle>
        <CardDescription>{statusDescription(interview.status)}</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {interview.status === "uploaded" && (
          <StatusRow icon={<Clock className="h-4 w-4" />} label="Upload complete. Waiting for worker..." />
        )}
        {interview.status === "processing" && (
          <StatusRow
            icon={<Loader2 className="h-4 w-4 animate-spin" />}
            label="Transcribing interview..."
          />
        )}
        {interview.status === "completed" && (
          <>
            <StatusRow
              icon={<CheckCircle2 className="h-4 w-4 text-emerald-600" />}
              label="Processing complete."
            />
            <div className="rounded-md border bg-muted/40 p-3 text-sm whitespace-pre-wrap">
              {interview.transcript?.raw_text || "No transcript text available."}
            </div>
          </>
        )}
        {interview.status === "failed" && (
          <>
            <StatusRow
              icon={<XCircle className="h-4 w-4 text-destructive" />}
              label="Processing failed."
            />
            {interview.failure_reason && (
              <p className="text-sm text-destructive">{interview.failure_reason}</p>
            )}
            {retryMutation.isError && (
              <p className="text-sm text-destructive">
                {retryMutation.error instanceof Error
                  ? retryMutation.error.message
                  : "Retry failed. Please try again."}
              </p>
            )}
          </>
        )}
      </CardContent>
      {interview.status === "failed" && (
        <CardFooter>
          <Button
            className="w-full"
            variant="outline"
            onClick={() => retryMutation.mutate()}
            disabled={retryMutation.isPending}
          >
            {retryMutation.isPending ? "Retrying..." : "Retry"}
          </Button>
        </CardFooter>
      )}
    </Card>
  )
}

function StatusRow({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      {icon}
      {label}
    </div>
  )
}

function statusDescription(status: string): string {
  switch (status) {
    case "uploaded":
      return "Queued for processing"
    case "processing":
      return "Processing in progress"
    case "completed":
      return "Transcript ready"
    case "failed":
      return "Something went wrong"
    default:
      return status
  }
}
