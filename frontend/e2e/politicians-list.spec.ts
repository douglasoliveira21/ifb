import { test, expect } from "@playwright/test";

test.describe("Listagem de Políticos", () => {
  test("exibe lista de políticos", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    const cards = await page.locator("a[href*='/politicos/']").count();
    expect(cards).toBeGreaterThan(0);
  });

  test("busca funciona", async ({ page }) => {
    await page.goto("/politicos");
    await page.fill('input[aria-label="Pesquisar político"]', "silva");
    await page.click('button:has-text("Pesquisar")');
    await page.waitForTimeout(2000);
    const url = page.url();
    expect(url).toContain("q=silva");
  });

  test("filtro por estado funciona", async ({ page }) => {
    await page.goto("/politicos");
    await page.selectOption('select[aria-label="Filtrar por estado"]', "SP");
    await page.waitForTimeout(2000);
    const url = page.url();
    expect(url).toContain("state=SP");
  });

  test("paginação funciona", async ({ page }) => {
    await page.goto("/politicos");
    await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
    const nextBtn = page.locator('button:has-text("Próxima")');
    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      await page.waitForTimeout(2000);
      expect(page.url()).toContain("page=2");
    }
  });
});
