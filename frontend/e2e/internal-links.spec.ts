import { test, expect } from "@playwright/test";

/**
 * Crawl all internal links from the homepage and verify none return 404/500.
 * Does NOT follow external links.
 */
test("All internal links from home are accessible", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  // Collect all internal links
  const links = await page.locator("a[href^='/']").evaluateAll((elements) =>
    [...new Set(elements.map((el) => el.getAttribute("href")).filter(Boolean))] as string[]
  );

  expect(links.length).toBeGreaterThan(0);

  const errors: string[] = [];

  for (const href of links) {
    // Skip anchors and query-only
    if (href === "#" || href.startsWith("/#")) continue;

    const response = await page.goto(href, { waitUntil: "domcontentloaded", timeout: 15000 });
    const status = response?.status() || 0;

    if (status >= 400) {
      errors.push(`${href} → ${status}`);
    }

    // Check for critical JS errors on page
    const bodyText = await page.locator("body").textContent();
    if (bodyText?.includes("Application error") || bodyText?.includes("Internal Server Error")) {
      errors.push(`${href} → Critical error in page content`);
    }
  }

  if (errors.length > 0) {
    throw new Error(`Broken internal links:\n${errors.join("\n")}`);
  }
});

test("Footer links are all valid", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });

  const footerLinks = await page.locator("footer a[href^='/']").evaluateAll((elements) =>
    [...new Set(elements.map((el) => el.getAttribute("href")).filter(Boolean))] as string[]
  );

  for (const href of footerLinks) {
    const response = await page.goto(href, { waitUntil: "domcontentloaded", timeout: 10000 });
    expect(response?.status(), `Footer link ${href} failed`).toBeLessThan(400);
  }
});
