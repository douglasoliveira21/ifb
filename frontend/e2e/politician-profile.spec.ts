import { test, expect } from "@playwright/test";

test.describe("Perfil do Político", () => {
  test("abre perfil de um político", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });
    const name = await page.locator("h1").textContent();
    expect(name).toBeTruthy();
    expect(name!.length).toBeGreaterThan(2);
  });

  test("abas são clicáveis", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });

    // Click Gastos tab
    await page.click('button:has-text("Gastos")');
    await page.waitForTimeout(2000);
    // Should show the expenses section or empty state
    const content = await page.textContent("body");
    expect(content).toMatch(/Gastos Parlamentares|Não há despesas|Nenhuma despesa/);
  });

  test("aba de visão geral exibe dados", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    await page.locator("a[href*='/politicos/']").first().click();
    await page.waitForSelector("h1", { timeout: 10000 });
    // Overview tab should show party/state info
    const content = await page.textContent("body");
    expect(content).toMatch(/Cargo|Partido|Estado|Dados/);
  });
});
