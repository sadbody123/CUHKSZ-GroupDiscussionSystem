import { apiRequest } from "./client";
import type {
  AutoRunRequest,
  AutoRunResponse,
  FeedbackResponse,
  RunNextTurnResponse,
  SubmitUserTurnRequest,
  SubmitUserTurnResponse
} from "./generated-adapters";

export async function submitUserTurn(
  sessionId: string,
  body: SubmitUserTurnRequest
): Promise<SubmitUserTurnResponse> {
  return apiRequest<SubmitUserTurnResponse>(`/sessions/${sessionId}/turns/user`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function runNextTurn(sessionId: string): Promise<RunNextTurnResponse> {
  return apiRequest<RunNextTurnResponse>(`/sessions/${sessionId}/run-next`, { method: "POST" });
}

export async function autoRunDiscussion(
  sessionId: string,
  body: AutoRunRequest
): Promise<AutoRunResponse> {
  return apiRequest<AutoRunResponse>(`/sessions/${sessionId}/auto-run`, {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function generateFeedback(sessionId: string): Promise<FeedbackResponse> {
  return apiRequest<FeedbackResponse>(`/sessions/${sessionId}/feedback`, { method: "POST" });
}

export async function cancelAutoRun(
  sessionId: string
): Promise<{ status: string; session_id: string }> {
  return apiRequest<{ status: string; session_id: string }>(`/sessions/${sessionId}/cancel-auto-run`, {
    method: "POST"
  });
}
