import { expect, test } from "@playwright/test";

test("real backend discussion path: create session and run-next", async ({ page }) => {
  await page.goto("/sessions");
  await expect(page.getByRole("heading", { name: "Discussion Console" })).toBeVisible();

  const snapshotSelect = page.getByLabel("Snapshot");
  await snapshotSelect.waitFor({ state: "visible" });
  await snapshotSelect.selectOption("dev_snapshot_v2");

  const topicSelect = page.getByLabel("Topic");
  await expect(topicSelect).toBeEnabled();
  const topicOptions = topicSelect.locator("option");
  await expect
    .poll(async () => topicOptions.count(), {
      message: "topic options should be loaded from backend"
    })
    .toBeGreaterThan(1);
  const firstTopicValue = await topicOptions.nth(1).getAttribute("value");
  expect(firstTopicValue).toBeTruthy();
  await topicSelect.selectOption(String(firstTopicValue));

  await page.getByRole("button", { name: "Create Session" }).click();
  await expect(page.getByRole("heading", { name: /Session / })).toBeVisible();

  const userInput = page.getByPlaceholder("Type user turn");
  await userInput.fill("Playwright real backend message.");
  await page.getByRole("button", { name: "Submit User Turn" }).click();
  await page.getByRole("button", { name: "Run Next Turn" }).click();

  await expect(page.getByRole("heading", { name: "Transcript (full, paginated)" })).toBeVisible();
  await expect(page.getByText("Playwright real backend message.")).toBeVisible();
});
