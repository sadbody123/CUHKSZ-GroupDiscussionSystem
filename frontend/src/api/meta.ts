import { apiRequest } from "./client";
import type { ProfileSummary, SnapshotSummary, TopicSummary } from "./generated-adapters";

export async function listSnapshots(): Promise<SnapshotSummary[]> {
  return apiRequest<SnapshotSummary[]>("/snapshots");
}

export async function listProfiles(): Promise<ProfileSummary[]> {
  return apiRequest<ProfileSummary[]>("/profiles");
}

export async function listTopics(snapshotId: string): Promise<TopicSummary[]> {
  const q = new URLSearchParams({ snapshot_id: snapshotId });
  return apiRequest<TopicSummary[]>(`/topics?${q.toString()}`);
}
