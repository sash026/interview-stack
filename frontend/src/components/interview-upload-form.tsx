"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"

import { uploadInterview } from "@/lib/api/interviews"
import {
  interviewUploadSchema,
  type InterviewUploadValues,
} from "@/lib/schemas/interview-upload"
import { InterviewStatus } from "@/components/interview-status"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export function InterviewUploadForm() {
  const [selectedFileName, setSelectedFileName] = useState<string | null>(
    null
  )
  const [fileInputKey, setFileInputKey] = useState(0)
  const [uploadedInterviewId, setUploadedInterviewId] = useState<
    string | null
  >(null)

  const form = useForm<InterviewUploadValues>({
    resolver: zodResolver(interviewUploadSchema),
    defaultValues: {
      title: "",
      notes: "",
    },
  })

  const uploadMutation = useMutation({
    mutationFn: uploadInterview,
  })

  function onSubmit(values: InterviewUploadValues) {
    uploadMutation.mutate(values, {
      onSuccess: (response) => {
        form.reset()
        setSelectedFileName(null)
        setFileInputKey((key) => key + 1)
        setUploadedInterviewId(response.id)
      },
    })
  }

  return (
    <div className="flex w-full max-w-lg flex-col gap-6">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Upload Interview</CardTitle>
          <CardDescription>
            Add an audio recording or paste raw text notes for a new
            interview.
          </CardDescription>
        </CardHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <CardContent className="flex flex-col gap-6">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Interview Name / Title</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="e.g. Candidate A - Round 1"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="audioFile"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Audio File</FormLabel>
                    <FormControl>
                      <Input
                        key={fileInputKey}
                        name={field.name}
                        onBlur={field.onBlur}
                        ref={field.ref}
                        type="file"
                        accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/x-m4a,audio/mp4"
                        onChange={(event) => {
                          const file = event.target.files?.[0]
                          field.onChange(file)
                          setSelectedFileName(file?.name ?? null)
                        }}
                      />
                    </FormControl>
                    <FormDescription>
                      Accepts .mp3, .wav, or .m4a files.
                      {selectedFileName ? ` Selected: ${selectedFileName}` : ""}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <div className="h-px flex-1 bg-border" />
                OR
                <div className="h-px flex-1 bg-border" />
              </div>

              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Text Notes</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Paste raw interview notes here..."
                        className="min-h-32"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {uploadMutation.isError && (
                <p className="text-sm text-destructive">
                  {uploadMutation.error instanceof Error
                    ? uploadMutation.error.message
                    : "Something went wrong. Please try again."}
                </p>
              )}
            </CardContent>
            <CardFooter>
              <Button
                type="submit"
                className="w-full"
                disabled={uploadMutation.isPending}
              >
                {uploadMutation.isPending ? "Uploading..." : "Upload Interview"}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </Card>
      {uploadedInterviewId && (
        <InterviewStatus interviewId={uploadedInterviewId} />
      )}
    </div>
  )
}
