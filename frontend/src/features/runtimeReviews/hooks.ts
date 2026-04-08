import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  applyEditedDraft,
  approveRuntimeReview,
  getRuntimeReview,
  getRuntimeReviewMetrics,
  listRuntimeReviews,
  rejectRuntimeReview,
  resumeRuntimeReview
} from "../../api/runtimeReviews";
import type {
  ApplyEditedDraftRequest,
  ApproveRuntimeReviewRequest,
  RejectRuntimeReviewRequest,
  ResumeRuntimeReviewRequest
} from "../../api/generated-adapters";

export const runtimeReviewKeys = {
  list: (status: string, sessionId?: string, topicId?: string) =>
    ["runtime-reviews", "list", status, sessionId || "", topicId || ""] as const,
  detail: (reviewId: string) => ["runtime-reviews", "detail", reviewId] as const,
  metrics: () => ["runtime-reviews", "metrics"] as const
};

export function useRuntimeReviewList(status: string, options?: { sessionId?: string; topicId?: string }) {
  return useQuery({
    queryKey: runtimeReviewKeys.list(status, options?.sessionId, options?.topicId),
    queryFn: () => listRuntimeReviews(status, options)
  });
}

export function useRuntimeReviewDetail(reviewId: string) {
  return useQuery({
    queryKey: runtimeReviewKeys.detail(reviewId),
    queryFn: () => getRuntimeReview(reviewId),
    enabled: Boolean(reviewId)
  });
}

export function useRuntimeReviewMetrics() {
  return useQuery({
    queryKey: runtimeReviewKeys.metrics(),
    queryFn: getRuntimeReviewMetrics
  });
}

function useInvalidateRuntimeReviewQueries() {
  const qc = useQueryClient();
  return () =>
    Promise.all([
      qc.invalidateQueries({ queryKey: ["runtime-reviews"] }),
      qc.invalidateQueries({ queryKey: runtimeReviewKeys.metrics() })
    ]);
}

export function useApproveRuntimeReview(reviewId: string) {
  const invalidate = useInvalidateRuntimeReviewQueries();
  return useMutation({
    mutationFn: (body: ApproveRuntimeReviewRequest) => approveRuntimeReview(reviewId, body),
    onSuccess: invalidate
  });
}

export function useRejectRuntimeReview(reviewId: string) {
  const invalidate = useInvalidateRuntimeReviewQueries();
  return useMutation({
    mutationFn: (body: RejectRuntimeReviewRequest) => rejectRuntimeReview(reviewId, body),
    onSuccess: invalidate
  });
}

export function useResumeRuntimeReview(reviewId: string) {
  const invalidate = useInvalidateRuntimeReviewQueries();
  return useMutation({
    mutationFn: (body: ResumeRuntimeReviewRequest) => resumeRuntimeReview(reviewId, body),
    onSuccess: invalidate
  });
}

export function useApplyEditedDraft(reviewId: string) {
  const invalidate = useInvalidateRuntimeReviewQueries();
  return useMutation({
    mutationFn: (body: ApplyEditedDraftRequest) => applyEditedDraft(reviewId, body),
    onSuccess: invalidate
  });
}
