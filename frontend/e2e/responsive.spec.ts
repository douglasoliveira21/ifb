import { test, expect } from "@playwright/test";

const pages = [
  { path: "/", name: "Home" },
  { path: "/politicos", name: "Listagem" },
  { path: "/login", name: "Login" },
  { path: "/sobre", name: "Sobre" },
  { path: "/transparencia", name: "Transparência" },
  { path: "/doar", name: "Doação" },
  { path: "/termos", name: "Termos" },
  { path: "/privacidade", name: "Privacidade" },
];

const viewports = [
  { width: 360, height: 800, name: "360px" },
  { width: 390, height: 844, name: "390px" },
  { width: 768, height: 1024, name: "768px" },
  { width: 1024, height: 768, name: "1024px" },
  { width: 1440, height: 900, name: "1440px" },
];

for (const page of pages) {
  for (const vp of viewports) {
    test(`${page.name} @ ${vp.name} — no horizontal overflow`, async ({ browser }) => {
      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const p = await context.newPage();
      await p.goto(page.path, { waitUntil: "networkidle" });

      // Check no horizontal scroll
      const bodyWidth = await p.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await p.evaluate(() => window.innerWidth);
      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1);

      // Check no JS errors
      const errors: string[] = [];
      p.on("pageerror", (err) => errors.push(err.message));
      expect(errors).toHaveLength(0);

      await context.close();
    });
  }
}
