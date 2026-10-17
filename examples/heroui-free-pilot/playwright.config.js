import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  fullyParallel: true,
  retries: 0,
  reporter: [["list"], ["html", { open: "never", outputFolder: "qa/playwright-report" }]],
  use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:4173", screenshot: "only-on-failure", trace: "retain-on-failure" },
  webServer: { command: "npm run dev", url: "http://127.0.0.1:4173", reuseExistingServer: false, timeout: 90_000 },
  outputDir: "qa/test-results"
});
