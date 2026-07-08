import { InterviewDetailView } from "@/components/interviews/interview-detail-view"

export default async function InterviewDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return <InterviewDetailView interviewId={id} />
}
