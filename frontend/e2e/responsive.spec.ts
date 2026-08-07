import { test, expect } from "@playwright/test";

/**
 * Responsiveness tests — verifies no horizontal overflow across viewports.
 * Runs on desktop, mobile, and tablet projects automatically via config.
 */

const ROUTES = [
  "/",
  "/politicos",
  "/ranking",
  "/noticias",
  "/metodologia",
  "/contato",
  "/sobre",
  "/transparencia",
  "/doar",
  "/termos",
  "/privacidade",
];

for (const route of ROUTES) {
  test(`${route} — no horizontal overflow`, async ({ page }) => {
    await page.goto(route, { waitUntil: "domcontentloaded" });

    const hasOverflow = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });

    expect(hasOverflow, `${route} has horizontal overflow`).toBeFalsy();
  });
}

test("Home — hero image hidden on mobile", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  // The hero image container has "hidden lg:block"
  // On mobile (iPhone 13, width 390), it should not be visible
  const viewport = page.viewportSize();
  if (viewport && viewport.width < 1024) {
    const heroImage = page.locator("img[alt='Congresso Nacional, Brasília']");
    await expect(heroImage).not.toBeVisible();
  }
});

test("Navigation — collapses on mobile", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  const viewport = page.viewportSize();
  if (viewport && viewport.width < 1024) {
    // Desktop nav should be hidden
    const nav = page.locator("nav.hidden.lg\\:flex");
    await expect(nav).not.toBeVisible();
  }
});
