# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive.spec.ts >> Home @ 1440px — no horizontal overflow
- Location: e2e\responsive.spec.ts:24:9

# Error details

```
Error: page.goto: Could not connect to server
Call log:
  - navigating to "http://localhost:3000/", waiting until "networkidle"

```

# Test source

```ts
  1  | import { test, expect } from "@playwright/test";
  2  | 
  3  | const pages = [
  4  |   { path: "/", name: "Home" },
  5  |   { path: "/politicos", name: "Listagem" },
  6  |   { path: "/login", name: "Login" },
  7  |   { path: "/sobre", name: "Sobre" },
  8  |   { path: "/transparencia", name: "Transparência" },
  9  |   { path: "/doar", name: "Doação" },
  10 |   { path: "/termos", name: "Termos" },
  11 |   { path: "/privacidade", name: "Privacidade" },
  12 | ];
  13 | 
  14 | const viewports = [
  15 |   { width: 360, height: 800, name: "360px" },
  16 |   { width: 390, height: 844, name: "390px" },
  17 |   { width: 768, height: 1024, name: "768px" },
  18 |   { width: 1024, height: 768, name: "1024px" },
  19 |   { width: 1440, height: 900, name: "1440px" },
  20 | ];
  21 | 
  22 | for (const page of pages) {
  23 |   for (const vp of viewports) {
  24 |     test(`${page.name} @ ${vp.name} — no horizontal overflow`, async ({ browser }) => {
  25 |       const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  26 |       const p = await context.newPage();
> 27 |       await p.goto(page.path, { waitUntil: "networkidle" });
     |               ^ Error: page.goto: Could not connect to server
  28 | 
  29 |       // Check no horizontal scroll
  30 |       const bodyWidth = await p.evaluate(() => document.body.scrollWidth);
  31 |       const viewportWidth = await p.evaluate(() => window.innerWidth);
  32 |       expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);
  33 | 
  34 |       // Check no JS errors
  35 |       const errors: string[] = [];
  36 |       p.on("pageerror", (err) => errors.push(err.message));
  37 |       expect(errors).toHaveLength(0);
  38 | 
  39 |       await context.close();
  40 |     });
  41 |   }
  42 | }
  43 | 
```