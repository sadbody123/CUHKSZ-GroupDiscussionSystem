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

// ---- Activation strategy API functions ----

export async function setActivationStrategy(sessionId: string, strategy: string): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}/activation-strategy`, {
    method: "PATCH",
    body: JSON.stringify({ strategy })
  });
}

export async function setAgentContextMode(sessionId: string, mode: string): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}/agent-context-mode`, {
    method: "PATCH",
    body: JSON.stringify({ mode })
  });
}

export async function setNextSpeaker(sessionId: string, participantId: string): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}/set-next-speaker`, {
    method: "POST",
    body: JSON.stringify({ participant_id: participantId })
  });
}

export async function toggleAutoMode(
  sessionId: string,
  enabled: boolean,
  delaySeconds?: number
): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}/auto-mode`, {
    method: "PATCH",
    body: JSON.stringify({ enabled, delay_seconds: delaySeconds })
  });
}

export async function setTalkativeness(
  sessionId: string,
  participantId: string,
  value: number
): Promise<SessionStatus> {
  return apiRequest<SessionStatus>(`/sessions/${sessionId}/participants/${participantId}/talkativeness`, {
    method: "PATCH",
    body: JSON.stringify({ participant_id: participantId, value })
  });
}
