import { expect, test } from "@playwright/test";

test("discussion flow create -> detail -> submit -> run-next", async ({ page }) => {
  await page.route("**/snapshots", async (route) => {
    await route.fulfill({ json: [{ snapshot_id: "dev_snapshot_v2", available: true }] });
  });
  await page.route("**/profiles", async (route) => {
    await route.fulfill({ json: [{ profile_id: "default" }] });
  });
  await page.route("**/topics?snapshot_id=dev_snapshot_v2", async (route) => {
    await route.fulfill({ json: [{ topic_id: "tc-campus-ai", topic: "Campus AI", tags: [] }] });
  });
  await page.route("**/runtime-reviews?status=pending&session_id=sess-e2e*", async (route) => {
    await route.fulfill({
      json: [
        {
          review_id: "rvw-e2e-1",
          session_id: "sess-e2e-1",
          run_id: "run-e2e-1",
          status: "pending",
          quality_flags: [],
          version: 1,
          allowed_actions: ["approve"],
          updated_at: "2026-01-01T00:00:00Z"
        }
      ]
    });
  });

  let turnCount = 1;
  await page.route("**/sessions", async (route, request) => {
    if (request.method() === "GET") {
      await route.fulfill({
        json: [
          {
            session_id: "sess-e2e-1",
            topic_id: "tc-campus-ai",
            phase: "discussion",
            turn_count: turnCount,
            provider_name: "mock"
          }
        ]
      });
      return;
    }
    if (request.method() === "POST") {
      await route.fulfill({
        json: {
          session_id: "sess-e2e-1",
          phase: "discussion",
          topic_id: "tc-campus-ai",
          provider_name: "mock",
          runtime_profile_id: "default",
          created_at: "2026-01-01T00:00:00Z"
        }
      });
      return;
    }
    await route.fallback();
  });

  await page.route("**/sessions/sess-e2e-1", async (route, request) => {
    if (request.method() === "GET") {
      await route.fulfill({
        json: {
          session_id: "sess-e2e-1",
          topic_id: "tc-campus-ai",
          phase: "discussion",
          runtime_profile_id: "default",
          retrieval_mode: "rule",
          has_indexes: true,
          provider_name: "mock",
          turn_count: turnCount,
          latest_turns: [],
          feedback_ready: false,
          coach_report_present: false,
          can_run_next: true,
          peek_next_role: "assistant"
        }
      });
      return;
    }
    await route.fallback();
  });

  await page.route("**/sessions/sess-e2e-1/transcript**", async (route) => {
    await route.fulfill({
      json: {
        session_id: "sess-e2e-1",
        total: turnCount,
        offset: 0,
        limit: 20,
        next_offset: null,
        items: [
          {
            turn_id: "t-user-1",
            sequence: 0,
            speaker_role: "user",
            text: "hello",
            created_at: "2026-01-01T00:00:00Z",
            manual_override: false,
            metadata: {}
          },
          ...(turnCount > 1
            ? [
                {
                  turn_id: "t-ai-1",
                  sequence: 1,
                  speaker_role: "assistant",
                  text: "assistant reply",
                  created_at: "2026-01-01T00:00:01Z",
                  manual_override: false,
                  metadata: {}
                }
              ]
            : [])
        ]
      }
    });
  });

  await page.route("**/sessions/sess-e2e-1/runtime-events**", async (route) => {
    await route.fulfill({
      json: {
        session_id: "sess-e2e-1",
        total: 1,
        offset: 0,
        limit: 20,
        next_offset: null,
        items: [
          {
            timestamp: "2026-01-01T00:00:01Z",
            run_id: "run-e2e-1",
            session_id: "sess-e2e-1",
            backend: "v2",
            node_name: "generate_turn",
            success: true,
            quality_flags: []
          }
        ]
      }
    });
  });

  await page.route("**/sessions/sess-e2e-1/turns/user", async (route) => {
    turnCount = Math.max(turnCount, 2);
    await route.fulfill({
      json: { session_id: "sess-e2e-1", turn_count: turnCount, new_turn: { text: "new user input" } }
    });
  });

  await page.route("**/sessions/sess-e2e-1/run-next", async (route) => {
    turnCount = Math.max(turnCount, 2);
    await route.fulfill({
      json: {
        next_role: "assistant",
        generated_reply: "assistant reply",
        generated_role: "assistant",
        updated_phase: "discussion",
        turn_count: turnCount,
        reply_metadata: {}
      }
    });
  });

  await page.goto("/");
  await page.getByRole("link", { name: "Discussions" }).click();
  await expect(page.getByRole("heading", { name: "Discussion Console" })).toBeVisible();
  await page.getByLabel("Snapshot").selectOption("dev_snapshot_v2");
  await page.getByLabel("Topic").selectOption("tc-campus-ai");
  await page.getByRole("button", { name: "Create Session" }).click();

  await expect(page.getByText("Session sess-e2e-1")).toBeVisible();
  await page.getByPlaceholder("Type user turn").fill("new user input");
  await page.getByRole("button", { name: "Submit User Turn" }).click();
  await page.getByRole("button", { name: "Run Next Turn" }).click();

  await expect(page.getByText("assistant reply")).toBeVisible();
});
