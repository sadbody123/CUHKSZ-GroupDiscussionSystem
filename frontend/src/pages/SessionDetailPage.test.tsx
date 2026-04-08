import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import SessionDetailPage from "./SessionDetailPage";

const submitMutate = vi.fn();
const nextMutate = vi.fn();
const autoMutate = vi.fn();
const feedbackMutate = vi.fn();

vi.mock("../features/sessions/hooks", () => ({
  useSessionStatus: () => ({
    isLoading: false,
    data: {
      session_id: "sess-1",
      topic_id: "topic-1",
      phase: "discussion",
      runtime_profile_id: "default",
      retrieval_mode: "rule",
      has_indexes: true,
      provider_name: "mock",
      turn_count: 1,
      latest_turns: [{ role: "user", text: "hello world", turn_id: "t1" }],
      feedback_ready: true,
      coach_report_present: false,
      can_run_next: true,
      peek_next_role: "assistant"
    }
  }),
  useSubmitUserTurn: () => ({ mutate: submitMutate, isPending: false }),
  useRunNextTurn: () => ({ mutate: nextMutate, isPending: false }),
  useAutoRunDiscussion: () => ({ mutate: autoMutate, isPending: false }),
  useGenerateFeedback: () => ({ mutate: feedbackMutate, isPending: false }),
  useSessionTranscript: () => ({
    isLoading: false,
    data: {
      pages: [
        {
          items: [{ turn_id: "t1", sequence: 0, speaker_role: "user", text: "hello world", metadata: {} }]
        }
      ]
    },
    hasNextPage: false,
    isFetchingNextPage: false,
    fetchNextPage: vi.fn(),
    error: null
  }),
  useSessionRuntimeEvents: () => ({
    isLoading: false,
    data: {
      pages: [
        {
          items: [
            {
              timestamp: "2026-01-01T00:00:00Z",
              run_id: "run-1",
              session_id: "sess-1",
              backend: "v2",
              node_name: "generate_turn",
              success: true,
              quality_flags: []
            }
          ]
        }
      ]
    },
    hasNextPage: false,
    isFetchingNextPage: false,
    fetchNextPage: vi.fn(),
    error: null
  })
}));

vi.mock("../features/runtimeReviews/hooks", () => ({
  useRuntimeReviewList: () => ({
    data: [{ review_id: "rvw-1", session_id: "sess-1", status: "pending" }],
    error: null
  })
}));

describe("SessionDetailPage", () => {
  it("renders transcript and triggers user turn mutation", () => {
    const qc = new QueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/sessions/sess-1"]}>
          <Routes>
            <Route path="/sessions/:sessionId" element={<SessionDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("Session sess-1")).toBeInTheDocument();
    expect(screen.getByText("hello world")).toBeInTheDocument();
    expect(screen.getByText("Runtime Timeline")).toBeInTheDocument();
    expect(screen.getByText("generate_turn")).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText("Type user turn"), { target: { value: "new user input" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit User Turn" }));
    expect(submitMutate).toHaveBeenCalledTimes(1);
  });
});
