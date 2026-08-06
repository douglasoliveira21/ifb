import { test, expect } from "@playwright/test";

test.describe("Páginas legais e institucionais", () => {
  test("/termos carrega corretamente", async ({ page }) => {
    await page.goto("/termos");
    await page.waitForSelector("h1", { timeout: 5000 });
    const title = await page.locator("h1").textContent();
    expect(title).toContain("Termos");
    const body = await page.textContent("body");
    expect(body).toContain("Finalidade");
    expect(body).toContain("inteligência artificial");
  });

  test("/privacidade carrega corretamente", async ({ page }) => {
    await page.goto("/privacidade");
    await page.waitForSelector("h1", { timeout: 5000 });
    const title = await page.locator("h1").textContent();
    expect(title).toContain("Privacidade");
    const body = await page.textContent("body");
    expect(body).toContain("LGPD");
    expect(body).toContain("cookies");
  });

  test("/sobre carrega corretamente", async ({ page }) => {
    await page.goto("/sobre");
    await page.waitForSelector("h1", { timeout: 5000 });
    const body = await page.textContent("body");
    expect(body).toContain("Missão");
    expect(body).toContain("apartidário");
  });

  test("/transparencia carrega corretamente", async ({ page }) => {
    await page.goto("/transparencia");
    await page.waitForSelector("h1", { timeout: 5000 });
    const body = await page.textContent("body");
    expect(body).toContain("Transparência");
  });

  test("/doar carrega corretamente", async ({ page }) => {
    await page.goto("/doar");
    await page.waitForSelector("h1", { timeout: 5000 });
    const body = await page.textContent("body");
    expect(body).toContain("Apoie");
    expect(body).toContain("homologação");
  });

  test("/login carrega corretamente", async ({ page }) => {
    await page.goto("/login");
    await page.waitForSelector("h1", { timeout: 5000 });
    const body = await page.textContent("body");
    expect(body).toContain("Entrar");
  });
});
