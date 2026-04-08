import { describe, expect, it, vi } from "vitest";

import { listRuntimeReviews } from "./runtimeReviews";

describe("runtimeReviews api client", () => {
  it("requests list endpoint with status filter", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => []
    });
    vi.stubGlobal("fetch", mock);
    await listRuntimeReviews("pending");
    expect(mock).toHaveBeenCalledTimes(1);
    const url = String(mock.mock.calls[0][0]);
    expect(url).toContain("/runtime-reviews?status=pending");
  });

  it("includes optional session filter in query", async () => {
    const mock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => []
    });
    vi.stubGlobal("fetch", mock);
    await listRuntimeReviews("pending", { sessionId: "sess-1" });
    const url = String(mock.mock.calls[0][0]);
    expect(url).toContain("session_id=sess-1");
  });
});
