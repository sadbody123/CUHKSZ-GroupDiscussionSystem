/**
 * Generated contract adapter layer.
 *
 * Page/API modules should import from here instead of importing generated types
 * directly. This keeps migration and compatibility changes localized.
 */

import type { components } from "./generated/openapi";

export type RuntimeReviewSummary = components["schemas"]["RuntimeReviewSummaryResponse"];
export type RuntimeReviewDetail = components["schemas"]["RuntimeReviewDetailResponse"];
export type RuntimeReviewMetrics = components["schemas"]["RuntimeReviewMetricsResponse"];
export type RuntimeReviewStatus = RuntimeReviewSummary["status"];

export type ApproveRuntimeReviewRequest = components["schemas"]["ApproveRuntimeReviewRequest"];
export type RejectRuntimeReviewRequest = components["schemas"]["RejectRuntimeReviewRequest"];
export type ResumeRuntimeReviewRequest = components["schemas"]["ResumeRuntimeReviewRequest"];
export type ApplyEditedDraftRequest = components["schemas"]["ApplyEditedDraftRequest"];

export type SessionListItem = components["schemas"]["SessionListItemResponse"];
export type CreateSessionRequest = components["schemas"]["CreateSessionRequest"];
export type CreateSessionResponse = components["schemas"]["CreateSessionResponse"];
export type SessionStatus = components["schemas"]["SessionStatusResponse"];
export type SessionTranscriptTurn = components["schemas"]["TranscriptTurnResponse"];
export type SessionTranscriptPage = components["schemas"]["SessionTranscriptResponse"];
export type SessionRuntimeEvent = components["schemas"]["RuntimeEventResponse"];
export type SessionRuntimeEventsPage = components["schemas"]["SessionRuntimeEventsResponse"];

export type SubmitUserTurnRequest = components["schemas"]["SubmitUserTurnRequest"];
export type SubmitUserTurnResponse = components["schemas"]["SubmitUserTurnResponse"];
export type RunNextTurnResponse = components["schemas"]["RunNextTurnResponse"];
export type AutoRunRequest = components["schemas"]["AutoRunRequest"];
export type AutoRunResponse = components["schemas"]["AutoRunResponse"];
export type FeedbackResponse = components["schemas"]["FeedbackResponse"];

export type SnapshotSummary = components["schemas"]["SnapshotSummaryResponse"];
export type TopicSummary = components["schemas"]["TopicSummaryResponse"];
export type ProfileSummary = components["schemas"]["ProfileSummaryResponse"];
