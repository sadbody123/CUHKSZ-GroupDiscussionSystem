import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import RuntimeReviewDetailPage from "./RuntimeReviewDetailPage";

vi.mock("../features/runtimeReviews/hooks", () => {
  const mutate = vi.fn();
  return {
    useRuntimeReviewDetail: () => ({
      isLoading: false,
      data: {
        review_id: "rvw-1",
        session_id: "sess-1",
        run_id: "run-1",
        status: "pending",
        quality_flags: ["too_short"],
        version: 3,
        allowed_actions: ["apply_edited_draft", "approve", "reject", "resume"],
        updated_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        draft_reply_text: "draft text",
        checkpoint_id: "ckpt-1",
        reason: "quality_interrupt",
        interrupt_reason: "quality_failed_after_max_repairs",
        review_decision_payload: {},
        notes: [],
        metadata: {}
      }
    }),
    useApproveRuntimeReview: () => ({ mutate, isPending: false }),
    useRejectRuntimeReview: () => ({ mutate, isPending: false }),
    useResumeRuntimeReview: () => ({ mutate, isPending: false }),
    useApplyEditedDraft: () => ({ mutate, isPending: false })
  };
});

describe("RuntimeReviewDetailPage", () => {
  it("renders editable draft area and action button", () => {
    const qc = new QueryClient();
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/runtime-reviews/rvw-1"]}>
          <Routes>
            <Route path="/runtime-reviews/:reviewId" element={<RuntimeReviewDetailPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(screen.getByText("rvw-1")).toBeInTheDocument();
    const input = screen.getByTestId("edited-draft-input");
    fireEvent.change(input, { target: { value: "edited draft text" } });
    expect(screen.getByRole("button", { name: "Apply Edited Draft" })).toBeEnabled();
  });
});
