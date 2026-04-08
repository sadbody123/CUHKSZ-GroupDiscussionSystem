import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "../App";

function mockResponse(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body
  });
}

describe("discussion console smoke", () => {
  it.skip("supports create -> detail -> submit/run path", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = String(init?.method || "GET").toUpperCase();

      if (url.includes("/snapshots") && method === "GET") {
        return mockResponse([{ snapshot_id: "dev_snapshot_v2", available: true }]);
      }
      if (url.includes("/profiles") && method === "GET") {
        return mockResponse([{ profile_id: "default" }]);
      }
      if (url.includes("/topics?snapshot_id=dev_snapshot_v2") && method === "GET") {
        return mockResponse([{ topic_id: "tc-campus-ai", topic: "Campus AI", tags: [] }]);
      }
      if (url.endsWith("/sessions") && method === "GET") {
        return mockResponse([]);
      }
      if (url.endsWith("/sessions") && method === "POST") {
        return mockResponse({
          session_id: "sess-1",
          phase: "discussion",
          topic_id: "tc-campus-ai",
          provider_name: "mock",
          runtime_profile_id: "default",
          created_at: "2026-01-01T00:00:00Z"
        });
      }
      if (url.includes("/sessions/sess-1/transcript") && method === "GET") {
        return mockResponse({
          session_id: "sess-1",
          total: 1,
          offset: 0,
          limit: 20,
          next_offset: null,
          items: [
            {
              turn_id: "t1",
              sequence: 0,
              speaker_role: "user",
              text: "hello from user",
              created_at: "2026-01-01T00:00:00Z",
              manual_override: false,
              metadata: {}
            }
          ]
        });
      }
      if (url.includes("/sessions/sess-1/runtime-events") && method === "GET") {
        return mockResponse({
          session_id: "sess-1",
          total: 1,
          offset: 0,
          limit: 20,
          next_offset: null,
          items: [
            {
              timestamp: "2026-01-01T00:00:01Z",
              run_id: "run-1",
              session_id: "sess-1",
              backend: "v2",
              node_name: "generate_turn",
              success: true,
              quality_flags: [],
              review_id: "rvw-1"
            }
          ]
        });
      }
      if (url.endsWith("/sessions/sess-1") && method === "GET") {
        return mockResponse({
          session_id: "sess-1",
          topic_id: "tc-campus-ai",
          phase: "discussion",
          runtime_profile_id: "default",
          retrieval_mode: "rule",
          has_indexes: true,
          provider_name: "mock",
          turn_count: 1,
          latest_turns: [],
          feedback_ready: false,
          coach_report_present: false,
          can_run_next: true,
          peek_next_role: "assistant"
        });
      }
      if (url.includes("/runtime-reviews?status=pending&session_id=sess-1") && method === "GET") {
        return mockResponse([
          {
            review_id: "rvw-1",
            session_id: "sess-1",
            run_id: "run-1",
            status: "pending",
            quality_flags: [],
            version: 1,
            allowed_actions: ["approve"],
            updated_at: "2026-01-01T00:00:01Z"
          }
        ]);
      }
      if (url.endsWith("/sessions/sess-1/turns/user") && method === "POST") {
        return mockResponse({ session_id: "sess-1", turn_count: 2, new_turn: { text: "new user input" } });
      }
      if (url.endsWith("/sessions/sess-1/run-next") && method === "POST") {
        return mockResponse({
          next_role: "assistant",
          generated_reply: "assistant reply",
          generated_role: "assistant",
          updated_phase: "discussion",
          turn_count: 3,
          reply_metadata: {}
        });
      }
      if (url.endsWith("/sessions/sess-1/auto-run") && method === "POST") {
        return mockResponse({ new_turns: [], session: { session_id: "sess-1" } });
      }
      if (url.endsWith("/sessions/sess-1/feedback") && method === "POST") {
        return mockResponse({
          session_id: "sess-1",
          topic_id: "tc-campus-ai",
          coach_text: "feedback text",
          strengths: [],
          risks: [],
          suggested_next_actions: [],
          feedback_packet: {},
          metadata: {}
        });
      }
      return mockResponse({ detail: `Unhandled ${method} ${url}` }, 404);
    });

    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/sessions"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );

    await waitFor(() => expect(screen.getByText("Discussion Console")).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Snapshot"), { target: { value: "dev_snapshot_v2" } });
    await waitFor(() => expect(screen.getByRole("option", { name: "tc-campus-ai" })).toBeInTheDocument());
    fireEvent.change(screen.getByLabelText("Topic"), { target: { value: "tc-campus-ai" } });
    fireEvent.click(screen.getByRole("button", { name: "Create Session" }));

    await waitFor(() => expect(screen.getByText("Session sess-1")).toBeInTheDocument());
    expect(screen.getByText("hello from user")).toBeInTheDocument();
    expect(screen.getByText("Runtime Timeline")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("Type user turn"), { target: { value: "new user input" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit User Turn" }));
    fireEvent.click(screen.getByRole("button", { name: "Run Next Turn" }));

    await waitFor(() => {
      const urls = fetchMock.mock.calls.map((c) => String(c[0]));
      expect(urls.some((u) => u.includes("/sessions/sess-1/turns/user"))).toBe(true);
      expect(urls.some((u) => u.includes("/sessions/sess-1/run-next"))).toBe(true);
    });
  });
});
