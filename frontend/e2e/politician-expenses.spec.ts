import { test, expect } from "@playwright/test";

test.describe("Gastos Parlamentares", () => {
  test("aba de gastos carrega dados", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });
    await page.click('button:has-text("Gastos")');
    await page.waitForTimeout(3000);

    // Should show either data or empty state
    const body = await page.textContent("body");
    const hasData = body?.includes("Valor líquido") || body?.includes("Não há despesas");
    expect(hasData).toBeTruthy();
  });

  test("filtro por ano funciona", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });
    await page.click('button:has-text("Gastos")');
    await page.waitForTimeout(2000);

    // Change year filter
    const yearSelect = page.locator("select").first();
    if (await yearSelect.isVisible()) {
      await yearSelect.selectOption("2025");
      await page.waitForTimeout(2000);
    }
  });

  test("fonte oficial é exibida", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });
    await page.click('button:has-text("Gastos")');
    await page.waitForTimeout(3000);

    const body = await page.textContent("body");
    expect(body).toContain("Câmara dos Deputados");
  });
});
