import { apiRequest } from "./client";
import type {
  CreateSessionRequest,
  CreateSessionResponse,
  SessionListItem,
  SessionRuntimeEventsPage,
  SessionStatus,
  SessionTranscriptPage
} from "./generated-adapters";

export async function listSessions(): Promise<SessionListItem[]> {
  return apiRequest<SessionListItem[]>("/sessions");
}

export async function createSession(body: CreateSessionRequest): Promise<CreateSessionResponse> {
  return apiRequest<CreateSessionResponse>("/sessions", {
    method: "POST",
    body: JSON.stringify(body)
  });
}

export async function getSessionStatus(sessionId: string): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}`);
}

export async function getSessionTranscript(
  sessionId: string,
  params: { offset?: number; limit?: number } = {}
): Promise<SessionTranscriptPage> {
  const q = new URLSearchParams();
  q.set("offset", String(params.offset ?? 0));
  q.set("limit", String(params.limit ?? 20));
  return apiRequest<SessionTranscriptPage>(`/sessions/${sessionId}/transcript?${q.toString()}`);
}

export async function getSessionRuntimeEvents(
  sessionId: string,
  params: { offset?: number; limit?: number; runId?: string } = {}
): Promise<SessionRuntimeEventsPage> {
  const q = new URLSearchParams();
  q.set("offset", String(params.offset ?? 0));
  q.set("limit", String(params.limit ?? 20));
  if (params.runId) q.set("run_id", params.runId);
  return apiRequest<SessionRuntimeEventsPage>(`/sessions/${sessionId}/runtime-events?${q.toString()}`);
}
