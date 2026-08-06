# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: politicians-list.spec.ts >> Listagem de Políticos >> busca funciona
- Location: e2e\politicians-list.spec.ts:11:7

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
  3  | test.describe("Listagem de Políticos", () => {
  4  |   test("exibe lista de políticos", async ({ page }) => {
  5  |     await page.goto("/politicos");
  6  |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  7  |     const cards = await page.locator("a[href*='/politicos/']").count();
  8  |     expect(cards).toBeGreaterThan(0);
  9  |   });
  10 | 
  11 |   test("busca funciona", async ({ page }) => {
> 12 |     await page.goto("/politicos");
     |                ^ Error: page.goto: Could not connect to server
  13 |     await page.fill('input[aria-label="Pesquisar político"]', "silva");
  14 |     await page.click('button:has-text("Pesquisar")');
  15 |     await page.waitForTimeout(2000);
  16 |     const url = page.url();
  17 |     expect(url).toContain("q=silva");
  18 |   });
  19 | 
  20 |   test("filtro por estado funciona", async ({ page }) => {
  21 |     await page.goto("/politicos");
  22 |     await page.selectOption('select[aria-label="Filtrar por estado"]', "SP");
  23 |     await page.waitForTimeout(2000);
  24 |     const url = page.url();
  25 |     expect(url).toContain("state=SP");
  26 |   });
  27 | 
  28 |   test("paginação funciona", async ({ page }) => {
  29 |     await page.goto("/politicos");
  30 |     await page.waitForSelector("a[href*='/politicos/']", { timeout: 10000 });
  31 |     const nextBtn = page.locator('button:has-text("Próxima")');
  32 |     if (await nextBtn.isVisible()) {
  33 |       await nextBtn.click();
  34 |       await page.waitForTimeout(2000);
  35 |       expect(page.url()).toContain("page=2");
  36 |     }
  37 |   });
  38 | });
  39 | 
```