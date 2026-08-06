# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: legal-pages.spec.ts >> Páginas legais e institucionais >> /login carrega corretamente
- Location: e2e\legal-pages.spec.ts:47:7

# Error details

```
Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/login
Call log:
  - navigating to "http://localhost:3000/login", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | test.describe("Páginas legais e institucionais", () => {
  4  |   test("/termos carrega corretamente", async ({ page }) => {
  5  |     await page.goto("/termos");
  6  |     await page.waitForSelector("h1", { timeout: 5000 });
  7  |     const title = await page.locator("h1").textContent();
  8  |     expect(title).toContain("Termos");
  9  |     const body = await page.textContent("body");
  10 |     expect(body).toContain("Finalidade");
  11 |     expect(body).toContain("inteligência artificial");
  12 |   });
  13 | 
  14 |   test("/privacidade carrega corretamente", async ({ page }) => {
  15 |     await page.goto("/privacidade");
  16 |     await page.waitForSelector("h1", { timeout: 5000 });
  17 |     const title = await page.locator("h1").textContent();
  18 |     expect(title).toContain("Privacidade");
  19 |     const body = await page.textContent("body");
  20 |     expect(body).toContain("LGPD");
  21 |     expect(body).toContain("cookies");
  22 |   });
  23 | 
  24 |   test("/sobre carrega corretamente", async ({ page }) => {
  25 |     await page.goto("/sobre");
  26 |     await page.waitForSelector("h1", { timeout: 5000 });
  27 |     const body = await page.textContent("body");
  28 |     expect(body).toContain("Missão");
  29 |     expect(body).toContain("apartidário");
  30 |   });
  31 | 
  32 |   test("/transparencia carrega corretamente", async ({ page }) => {
  33 |     await page.goto("/transparencia");
  34 |     await page.waitForSelector("h1", { timeout: 5000 });
  35 |     const body = await page.textContent("body");
  36 |     expect(body).toContain("Transparência");
  37 |   });
  38 | 
  39 |   test("/doar carrega corretamente", async ({ page }) => {
  40 |     await page.goto("/doar");
  41 |     await page.waitForSelector("h1", { timeout: 5000 });
  42 |     const body = await page.textContent("body");
  43 |     expect(body).toContain("Apoie");
  44 |     expect(body).toContain("homologação");
  45 |   });
  46 | 
  47 |   test("/login carrega corretamente", async ({ page }) => {
> 48 |     await page.goto("/login");
     |                ^ Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/login
  49 |     await page.waitForSelector("h1", { timeout: 5000 });
  50 |     const body = await page.textContent("body");
  51 |     expect(body).toContain("Entrar");
  52 |   });
  53 | });
  54 | 
```