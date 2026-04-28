import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { autoRunDiscussion, cancelAutoRun, generateFeedback, runNextTurn, submitUserTurn } from "../../api/discussion";
import { listProfiles, listSnapshots, listTopics } from "../../api/meta";
import { createSession, getSessionRuntimeEvents, getSessionStatus, getSessionTranscript, listSessions, setActivationStrategy, setAgentContextMode, setNextSpeaker, setTalkativeness, toggleAutoMode } from "../../api/sessions";
import type { AutoRunRequest, CreateSessionRequest, SubmitUserTurnRequest } from "../../api/generated-adapters";

export const sessionKeys = {
  list: () => ["sessions", "list"] as const,
  detail: (sessionId: string) => ["sessions", "detail", sessionId] as const,
  transcript: (sessionId: string, pageSize: number) => ["sessions", "transcript", sessionId, pageSize] as const,
  runtimeEvents: (sessionId: string, runId: string | undefined, pageSize: number) =>
    ["sessions", "runtime-events", sessionId, runId || "", pageSize] as const,
  snapshots: () => ["sessions", "snapshots"] as const,
  topics: (snapshotId: string) => ["sessions", "topics", snapshotId] as const,
  profiles: () => ["sessions", "profiles"] as const
};

export function useSessionList() {
  return useQuery({
    queryKey: sessionKeys.list(),
    queryFn: listSessions
  });
}

export function useCreateSession() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateSessionRequest) => createSession(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: sessionKeys.list() })
  });
}

export function useSessionStatus(sessionId: string) {
  return useQuery({
    queryKey: sessionKeys.detail(sessionId),
    queryFn: () => getSessionStatus(sessionId),
    enabled: Boolean(sessionId)
  });
}

export function useSessionTranscript(sessionId: string, pageSize = 20) {
  return useInfiniteQuery({
    queryKey: sessionKeys.transcript(sessionId, pageSize),
    queryFn: ({ pageParam }) => getSessionTranscript(sessionId, { offset: pageParam as number, limit: pageSize }),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.next_offset ?? undefined,
    enabled: Boolean(sessionId)
  });
}

export function useSessionRuntimeEvents(sessionId: string, runId?: string, pageSize = 20) {
  return useInfiniteQuery({
    queryKey: sessionKeys.runtimeEvents(sessionId, runId, pageSize),
    queryFn: ({ pageParam }) =>
      getSessionRuntimeEvents(sessionId, { offset: pageParam as number, limit: pageSize, runId }),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.next_offset ?? undefined,
    enabled: Boolean(sessionId)
  });
}

export function useSnapshots() {
  return useQuery({
    queryKey: sessionKeys.snapshots(),
    queryFn: listSnapshots
  });
}

export function useProfiles() {
  return useQuery({
    queryKey: sessionKeys.profiles(),
    queryFn: listProfiles
  });
}

export function useTopics(snapshotId: string) {
  return useQuery({
    queryKey: sessionKeys.topics(snapshotId),
    queryFn: () => listTopics(snapshotId),
    enabled: Boolean(snapshotId)
  });
}

function useInvalidateSessionDetail(sessionId: string) {
  const qc = useQueryClient();
  return () =>
    Promise.all([
      qc.invalidateQueries({ queryKey: sessionKeys.detail(sessionId) }),
      qc.invalidateQueries({ queryKey: ["sessions", "transcript", sessionId] }),
      qc.invalidateQueries({ queryKey: ["sessions", "runtime-events", sessionId] }),
      qc.invalidateQueries({ queryKey: sessionKeys.list() }),
      qc.invalidateQueries({ queryKey: ["runtime-reviews"] })
    ]);
}

export function useSubmitUserTurn(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (body: SubmitUserTurnRequest) => submitUserTurn(sessionId, body),
    onSuccess: invalidate
  });
}

export function useRunNextTurn(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: () => runNextTurn(sessionId),
    onSuccess: invalidate
  });
}

export function useAutoRunDiscussion(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (body: AutoRunRequest) => autoRunDiscussion(sessionId, body),
    onSuccess: invalidate
  });
}

export function useGenerateFeedback(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: () => generateFeedback(sessionId),
    onSuccess: invalidate
  });
}

export function useCancelAutoRun(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: () => cancelAutoRun(sessionId),
    onSuccess: invalidate
  });
}

// ---- Activation strategy hooks ----

export function useSetActivationStrategy(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (strategy: string) => setActivationStrategy(sessionId, strategy),
    onSuccess: invalidate
  });
}

export function useSetAgentContextMode(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (mode: string) => setAgentContextMode(sessionId, mode),
    onSuccess: invalidate
  });
}

export function useSetNextSpeaker(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (participantId: string) => setNextSpeaker(sessionId, participantId),
    onSuccess: invalidate
  });
}

export function useToggleAutoMode(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (args: { enabled: boolean; delaySeconds?: number }) =>
      toggleAutoMode(sessionId, args.enabled, args.delaySeconds),
    onSuccess: invalidate
  });
}

export function useSetTalkativeness(sessionId: string) {
  const invalidate = useInvalidateSessionDetail(sessionId);
  return useMutation({
    mutationFn: (args: { participantId: string; value: number }) =>
      setTalkativeness(sessionId, args.participantId, args.value),
    onSuccess: invalidate
  });
}
