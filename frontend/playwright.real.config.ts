import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e-real",
  fullyParallel: false,
  reporter: "list",
  timeout: 120000,
  expect: { timeout: 15000 },
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry"
  },
  webServer: [
    {
      command: "python scripts/run_real_backend_e2e.py",
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
      timeout: 180000,
      env: {
        AGENT_RUNTIME_BACKEND: "v2"
      }
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 4173",
      url: "http://127.0.0.1:4173",
      reuseExistingServer: true,
      timeout: 120000,
      env: {
        VITE_API_BASE_URL: "http://127.0.0.1:8000"
      }
    }
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ]
});
