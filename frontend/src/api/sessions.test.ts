import { describe, expect, it, vi } from "vitest";

import { createSession, getSessionRuntimeEvents, getSessionStatus, getSessionTranscript, listSessions } from "./sessions";

describe("sessions api client", () => {
  it("requests sessions list", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => []
    });
    vi.stubGlobal("fetch", mock);
    await listSessions();
    expect(String(mock.mock.calls[0][0])).toContain("/sessions");
  });

  it("posts create session payload", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ session_id: "sess-1", phase: "discussion", provider_name: "mock", runtime_profile_id: "default", created_at: "" })
    });
    vi.stubGlobal("fetch", mock);
    await createSession({ snapshot_id: "snap-1", topic_id: "topic-1" });
    const [, init] = mock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(String(init.body)).toContain('"snapshot_id":"snap-1"');
  });

  it("gets session detail by id", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ session_id: "sess-1", phase: "discussion", runtime_profile_id: "default", retrieval_mode: "rule", has_indexes: true, provider_name: "mock", turn_count: 0, latest_turns: [], feedback_ready: false, coach_report_present: false, can_run_next: true })
    });
    vi.stubGlobal("fetch", mock);
    await getSessionStatus("sess-1");
    expect(String(mock.mock.calls[0][0])).toContain("/sessions/sess-1");
  });

  it("queries transcript endpoint with pagination params", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ session_id: "sess-1", total: 0, offset: 0, limit: 20, items: [] })
    });
    vi.stubGlobal("fetch", mock);
    await getSessionTranscript("sess-1", { offset: 10, limit: 5 });
    expect(String(mock.mock.calls[0][0])).toContain("/sessions/sess-1/transcript?offset=10&limit=5");
  });

  it("queries runtime events endpoint with run filter", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ session_id: "sess-1", total: 0, offset: 0, limit: 20, items: [] })
    });
    vi.stubGlobal("fetch", mock);
    await getSessionRuntimeEvents("sess-1", { offset: 0, limit: 20, runId: "run-1" });
    expect(String(mock.mock.calls[0][0])).toContain("/sessions/sess-1/runtime-events?offset=0&limit=20&run_id=run-1");
  });
});
