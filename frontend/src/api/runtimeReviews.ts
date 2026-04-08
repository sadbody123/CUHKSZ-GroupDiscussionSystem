import { apiRequest } from "./client";
import type {
  ApplyEditedDraftRequest,
  ApproveRuntimeReviewRequest,
  RejectRuntimeReviewRequest,
  ResumeRuntimeReviewRequest,
  RuntimeReviewDetail,
  RuntimeReviewMetrics,
  RuntimeReviewSummary
} from "./generated-adapters";

export async function listRuntimeReviews(
  status = "pending",
  options?: { sessionId?: string; topicId?: string }
): Promise<RuntimeReviewSummary[]> {
  const query = new URLSearchParams({ status });
  if (options?.sessionId) query.set("session_id", options.sessionId);
  if (options?.topicId) query.set("topic_id", options.topicId);
  return apiRequest<RuntimeReviewSummary[]>(`/runtime-reviews?${query.toString()}`);
}

export async function getRuntimeReview(reviewId: string): Promise<RuntimeReviewDetail> {
  return apiRequest<RuntimeReviewDetail>(`/runtime-reviews/${reviewId}`);
}

export async function approveRuntimeReview(
  reviewId: string,
  body: ApproveRuntimeReviewRequest
): Promise<{ review: RuntimeReviewDetail; result: Record<string, unknown> }> {
  return apiRequest(`/runtime-reviews/${reviewId}/approve`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function rejectRuntimeReview(
  reviewId: string,
  body: RejectRuntimeReviewRequest
): Promise<{ review: RuntimeReviewDetail; result: Record<string, unknown> }> {
  return apiRequest(`/runtime-reviews/${reviewId}/reject`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function resumeRuntimeReview(
  reviewId: string,
  body: ResumeRuntimeReviewRequest
): Promise<Record<string, unknown>> {
  return apiRequest(`/runtime-reviews/${reviewId}/resume`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function applyEditedDraft(
  reviewId: string,
  body: ApplyEditedDraftRequest
): Promise<Record<string, unknown>> {
  return apiRequest(`/runtime-reviews/${reviewId}/apply-edited-draft`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function getRuntimeReviewMetrics(): Promise<RuntimeReviewMetrics> {
  return apiRequest<RuntimeReviewMetrics>("/runtime-reviews/metrics/summary");
}
