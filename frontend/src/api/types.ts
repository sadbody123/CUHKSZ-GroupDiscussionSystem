export type RuntimeReviewStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "resumed"
  | "resolved";

export interface RuntimeReviewSummary {
  review_id: string;
  session_id: string;
  run_id: string;
  topic_id?: string | null;
  status: RuntimeReviewStatus;
  interrupt_reason?: string | null;
  quality_flags: string[];
  version: number;
  allowed_actions: string[];
  updated_at: string;
}

export interface RuntimeReviewDetail extends RuntimeReviewSummary {
  checkpoint_id?: string | null;
  reason?: string | null;
  draft_reply_text?: string | null;
  draft_reply_summary?: string | null;
  review_decision_payload: Record<string, unknown>;
  notes: string[];
  resolved_by?: string | null;
  updated_by?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface RuntimeReviewMetrics {
  created_review_count: number;
  pending_review_count: number;
  resolved_review_count: number;
  interrupt_rate: number;
  repair_rate: number;
  manual_override_count: number;
}

export interface SessionListItem {
  session_id: string;
  topic_id?: string | null;
  phase: string;
  turn_count: number;
  provider_name: string;
  learner_id?: string | null;
}

export interface CreateSessionRequest {
  snapshot_id: string;
  topic_id: string;
  user_stance?: string | null;
  provider_name?: string | null;
  model_name?: string | null;
  max_discussion_turns?: number | null;
  runtime_profile_id?: string | null;
}

export interface CreateSessionResponse {
  session_id: string;
  phase: string;
  topic_id?: string | null;
  provider_name: string;
  runtime_profile_id: string;
  created_at: string;
}

export interface SessionStatus {
  session_id: string;
  topic_id?: string | null;
  phase: string;
  runtime_profile_id: string;
  retrieval_mode: string;
  has_indexes: boolean;
  provider_name: string;
  model_name?: string | null;
  turn_count: number;
  latest_turns: Array<Record<string, unknown>>;
  feedback_ready: boolean;
  coach_report_present: boolean;
  coach_text_preview?: string | null;
  can_run_next: boolean;
  peek_next_role?: string | null;
}

export interface SessionTranscriptTurn {
  turn_id: string;
  sequence: number;
  speaker_role: string;
  text: string;
  created_at: string;
  manual_override: boolean;
  review_id?: string | null;
  run_id?: string | null;
  metadata: Record<string, unknown>;
}

export interface SessionTranscriptPage {
  session_id: string;
  total: number;
  offset: number;
  limit: number;
  next_offset?: number | null;
  items: SessionTranscriptTurn[];
}

export interface SessionRuntimeEvent {
  timestamp: string;
  run_id: string;
  session_id: string;
  backend: string;
  node_name: string;
  next_actor?: string | null;
  stop_reason?: string | null;
  success: boolean;
  error_summary?: string | null;
  trace_id?: string | null;
  checkpoint_id?: string | null;
  quality_decision?: string | null;
  interrupt_reason?: string | null;
  repair_count?: number | null;
  quality_flags: string[];
  review_id?: string | null;
  policy_id?: string | null;
}

export interface SessionRuntimeEventsPage {
  session_id: string;
  run_id?: string | null;
  total: number;
  offset: number;
  limit: number;
  next_offset?: number | null;
  items: SessionRuntimeEvent[];
}

export interface SubmitUserTurnRequest {
  text: string;
}

export interface SubmitUserTurnResponse {
  session_id: string;
  turn_count: number;
  new_turn: Record<string, unknown>;
}

export interface RunNextTurnResponse {
  next_role: string;
  generated_reply?: string | null;
  generated_role?: string | null;
  updated_phase: string;
  turn_count: number;
  reply_metadata: Record<string, unknown>;
}

export interface AutoRunRequest {
  max_steps: number;
}

export interface AutoRunResponse {
  new_turns: Array<Record<string, unknown>>;
  session: Record<string, unknown>;
}

export interface FeedbackResponse {
  session_id: string;
  topic_id?: string | null;
  coach_text: string;
  strengths: string[];
  risks: string[];
  suggested_next_actions: string[];
  feedback_packet: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface SnapshotSummary {
  snapshot_id: string;
  created_at?: string | null;
  available: boolean;
}

export interface TopicSummary {
  topic_id: string;
  topic: string;
  summary?: string | null;
  tags: string[];
}

export interface ProfileSummary {
  profile_id: string;
  description?: string | null;
}

export interface ApproveRuntimeReviewRequest {
  action: "approve" | "reject";
  expected_version?: number;
  updated_by?: string;
  payload?: Record<string, unknown>;
}

export interface RejectRuntimeReviewRequest {
  reason?: string;
  expected_version?: number;
  updated_by?: string;
}

export interface ResumeRuntimeReviewRequest {
  additional_steps: number;
}

export interface ApplyEditedDraftRequest {
  edited_text: string;
  expected_version?: number;
  updated_by?: string;
  note?: string;
  resume_after_apply?: boolean;
  additional_steps?: number;
}
