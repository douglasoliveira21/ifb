import { test, expect } from "@playwright/test";

/**
 * Tests for /noticias and /noticias/[id] pages.
 */

test.describe("News Pages", () => {
  test("/noticias — loads without error", async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    await page.goto("/noticias", { waitUntil: "domcontentloaded" });
    expect(errors).toHaveLength(0);

    // Should show either news list or empty state
    const hasItems = await page.locator("article").count();
    const hasEmpty = await page.getByText("Nenhuma notícia publicada").count();
    expect(hasItems + hasEmpty).toBeGreaterThan(0);
  });

  test("/noticias/invalid-id — shows not found state", async ({ page }) => {
    await page.goto("/noticias/00000000-0000-0000-0000-000000000000", { waitUntil: "domcontentloaded" });
    // Should show error or not found
    await page.waitForTimeout(2000);
    const body = await page.locator("body").textContent();
    const isNotFound = body?.includes("não encontrada") || body?.includes("não aprovada");
    expect(isNotFound).toBeTruthy();
  });

  test("/noticias/[id] — approved news shows classification", async ({ page }) => {
    // First check if there are any news
    await page.goto("/noticias", { waitUntil: "networkidle" });
    const firstLink = page.locator("a[href^='/noticias/']").first();

    if (await firstLink.isVisible()) {
      await firstLink.click();
      await page.waitForLoadState("domcontentloaded");

      // Should show classification details
      await expect(page.getByText("Resumo IFB").or(page.getByText("Sentimento"))).toBeVisible();
      await expect(page.getByText("Ler matéria original")).toBeVisible();

      // Should have methodology link
      await expect(page.getByRole("link", { name: /metodologia/i })).toBeVisible();

      // Should have AI disclaimer
      await expect(page.getByText(/inteligência artificial/i)).toBeVisible();
    }
  });
});
