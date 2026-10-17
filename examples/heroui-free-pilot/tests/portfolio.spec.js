import { test, expect } from "@playwright/test";
import fs from "node:fs";

const widths = [360,390,768,1440];

test("free HeroUI renders actual buttons and filters synthetic surfaces", async ({ page }) => {
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "One foundation. Distinct identities." })).toBeVisible();
  await expect(page.locator('[data-testid="venture-card"]')).toHaveCount(5);
  await page.getByRole("button", { name: "Learning", exact: true }).click();
  await expect(page.locator('[data-testid="venture-card"]')).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "LVL7 Learning" })).toBeVisible();
  await page.getByRole("button", { name: "Inspect LVL7 Learning" }).click();
  await expect(page.getByRole("heading", { name: "LVL7 Learning" })).toHaveCount(2);
  await page.getByRole("button", { name: /Save this design direction/ }).click();
  await expect(page.getByRole("button", { name: /Saved to local selection/ })).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("searchbox", { name: "Search product surfaces" }).fill("not a real category");
  await expect(page.getByText("No matching surfaces.")).toBeVisible();
  await page.getByRole("button", { name: "Reset view" }).click();
  await expect(page.locator('[data-testid="venture-card"]')).toHaveCount(5);
  expect(await page.locator("button.button").count()).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

for (const width of widths) {
  test(`responsive original layout + real controls ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const errors = [];
    page.on("pageerror", e => errors.push(e.message));
    await page.goto("/");
    await expect(page.locator('[data-testid="venture-card"]')).toHaveCount(5);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.getByRole("button", { name: "Services", exact: true }).click();
    await expect(page.locator('[data-testid="venture-card"]')).toHaveCount(1);
    await page.getByRole("button", { name: "Inspect Tirisano Travel" }).click();
    await expect(page.getByRole("heading", { name: "Tirisano Travel" })).toHaveCount(2);
    expect(errors).toEqual([]);
    fs.mkdirSync("qa/screenshots",{recursive:true});
    await page.screenshot({ path: `qa/screenshots/viewport-${width}.png`, fullPage:true });
  });
}

test("reduced-motion + keyboard focus + no external requests", async ({ page }) => {
  await page.emulateMedia({ reducedMotion:"reduce" });
  const outbound = [];
  page.on("request", r => { if (!r.url().startsWith("http://127.0.0.1:4173/")) outbound.push(r.url()); });
  await page.goto("/");
  await page.keyboard.press("Tab");
  expect(await page.evaluate(() => document.activeElement?.tagName)).toMatch(/^(A|BUTTON|INPUT)$/);
  const focused = await page.evaluate(() => getComputedStyle(document.activeElement).outlineStyle);
  expect(focused).not.toBe("none");
  const motion = await page.locator(".surface-card").first().evaluate(el => getComputedStyle(el).transitionDuration);
  expect(motion).toMatch(/0\.00001s|0s|1e-05s/);
  expect(outbound).toEqual([]);
});
