# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: politician-profile.spec.ts >> Perfil do Político >> aba de visão geral exibe dados
- Location: e2e\politician-profile.spec.ts:28:7

# Error details

```
Error: page.goto: Could not connect to server
Call log:
  - navigating to "http://localhost:3000/politicos", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Perfil do Político", () => {
  4  |   test("abre perfil de um político", async ({ page }) => {
  5  |     await page.goto("/politicos");
  6  |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  7  |     await page.locator("a[href*='/politicos/']").first().click();
  8  |     await page.waitForSelector("h1", { timeout: 10000 });
  9  |     const name = await page.locator("h1").textContent();
  10 |     expect(name).toBeTruthy();
  11 |     expect(name!.length).toBeGreaterThan(2);
  12 |   });
  13 | 
  14 |   test("abas são clicáveis", async ({ page }) => {
  15 |     await page.goto("/politicos");
  16 |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  17 |     await page.locator("a[href*='/politicos/']").first().click();
  18 |     await page.waitForSelector("h1", { timeout: 10000 });
  19 | 
  20 |     // Click Gastos tab
  21 |     await page.click('button:has-text("Gastos")');
  22 |     await page.waitForTimeout(2000);
  23 |     // Should show the expenses section or empty state
  24 |     const content = await page.textContent("body");
  25 |     expect(content).toMatch(/Gastos Parlamentares|Não há despesas|Nenhuma despesa/);
  26 |   });
  27 | 
  28 |   test("aba de visão geral exibe dados", async ({ page }) => {
> 29 |     await page.goto("/politicos");
     |                ^ Error: page.goto: Could not connect to server
  30 |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  31 |     await page.locator("a[href*='/politicos/']").first().click();
  32 |     await page.waitForSelector("h1", { timeout: 10000 });
  33 |     // Overview tab should show party/state info
  34 |     const content = await page.textContent("body");
  35 |     expect(content).toMatch(/Cargo|Partido|Estado|Dados/);
  36 |   });
  37 | });
  38 | 
```