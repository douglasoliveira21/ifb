# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: politician-expenses.spec.ts >> Gastos Parlamentares >> fonte oficial é exibida
- Location: e2e\politician-expenses.spec.ts:34:7

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
  3  | test.describe("Gastos Parlamentares", () => {
  4  |   test("aba de gastos carrega dados", async ({ page }) => {
  5  |     await page.goto("/politicos");
  6  |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  7  |     await page.locator("a[href*='/politicos/']").first().click();
  8  |     await page.waitForSelector("h1", { timeout: 10000 });
  9  |     await page.click('button:has-text("Gastos")');
  10 |     await page.waitForTimeout(3000);
  11 | 
  12 |     // Should show either data or empty state
  13 |     const body = await page.textContent("body");
  14 |     const hasData = body?.includes("Valor líquido") || body?.includes("Não há despesas");
  15 |     expect(hasData).toBeTruthy();
  16 |   });
  17 | 
  18 |   test("filtro por ano funciona", async ({ page }) => {
  19 |     await page.goto("/politicos");
  20 |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  21 |     await page.locator("a[href*='/politicos/']").first().click();
  22 |     await page.waitForSelector("h1", { timeout: 10000 });
  23 |     await page.click('button:has-text("Gastos")');
  24 |     await page.waitForTimeout(2000);
  25 | 
  26 |     // Change year filter
  27 |     const yearSelect = page.locator("select").first();
  28 |     if (await yearSelect.isVisible()) {
  29 |       await yearSelect.selectOption("2025");
  30 |       await page.waitForTimeout(2000);
  31 |     }
  32 |   });
  33 | 
  34 |   test("fonte oficial é exibida", async ({ page }) => {
> 35 |     await page.goto("/politicos");
     |                ^ Error: page.goto: Could not connect to server
  36 |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  37 |     await page.locator("a[href*='/politicos/']").first().click();
  38 |     await page.waitForSelector("h1", { timeout: 10000 });
  39 |     await page.click('button:has-text("Gastos")');
  40 |     await page.waitForTimeout(3000);
  41 | 
  42 |     const body = await page.textContent("body");
  43 |     expect(body).toContain("Câmara dos Deputados");
  44 |   });
  45 | });
  46 | 
```