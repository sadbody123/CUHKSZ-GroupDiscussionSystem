import { expect, test } from "@playwright/test";

test("review flow open detail and apply edited draft", async ({ page }) => {
  let version = 3;
  const reviewId = "rvw-e2e-1";

  await page.route("**/runtime-reviews/metrics/summary", async (route) => {
    await route.fulfill({
      json: {
        created_review_count: 1,
        pending_review_count: 1,
        resolved_review_count: 0,
        interrupt_rate: 1.0,
        repair_rate: 0.0,
        manual_override_count: 0
      }
    });
  });

  await page.route("**/runtime-reviews?status=pending**", async (route) => {
    await route.fulfill({
      json: [
        {
          review_id: reviewId,
          session_id: "sess-e2e-1",
          run_id: "run-e2e-1",
          topic_id: "tc-campus-ai",
          status: "pending",
          interrupt_reason: "quality_failed_after_max_repairs",
          quality_flags: ["too_short"],
          version,
          allowed_actions: ["apply_edited_draft", "approve", "reject", "resume"],
          updated_at: "2026-01-01T00:00:00Z"
        }
      ]
    });
  });

  await page.route(`**/runtime-reviews/${reviewId}`, async (route, request) => {
    if (request.method() !== "GET") return route.fallback();
    await route.fulfill({
      json: {
        review_id: reviewId,
        session_id: "sess-e2e-1",
        run_id: "run-e2e-1",
        checkpoint_id: "ckpt-1",
        topic_id: "tc-campus-ai",
        status: "pending",
        reason: "quality_interrupt",
        interrupt_reason: "quality_failed_after_max_repairs",
        quality_flags: ["too_short"],
        draft_reply_text: "draft text",
        draft_reply_summary: "draft text",
        version,
        allowed_actions: ["apply_edited_draft", "approve", "reject", "resume"],
        review_decision_payload: {},
        notes: [],
        metadata: {},
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z"
      }
    });
  });

  await page.route(`**/runtime-reviews/${reviewId}/apply-edited-draft`, async (route, request) => {
    if (request.method() !== "POST") return route.fallback();
    version += 1;
    const postBody = request.postDataJSON() as { edited_text?: string };
    await route.fulfill({
      json: {
        review: {
          review_id: reviewId,
          session_id: "sess-e2e-1",
          run_id: "run-e2e-1",
          status: "approved",
          quality_flags: ["too_short"],
          version,
          allowed_actions: ["resume", "resolve"],
          updated_at: "2026-01-01T00:00:02Z"
        },
        applied_turn_id: "manual-assistant-2",
        preview_text: postBody.edited_text || ""
      }
    });
  });

  await page.goto("/runtime-reviews");
  await expect(page.getByRole("heading", { name: "Runtime Reviews" })).toBeVisible();
  await page.getByRole("link", { name: reviewId }).click();
  await expect(page.getByText(reviewId)).toBeVisible();
  await page.getByTestId("edited-draft-input").fill("edited draft from playwright");
  await page.getByRole("button", { name: "Apply Edited Draft" }).click();

  await expect(page.getByRole("button", { name: "Apply Edited Draft" })).toBeVisible();
});
