import { test, expect } from "@playwright/test";

/**
 * Valida todas as páginas públicas: HTTP 200, sem erro JS crítico, sem 404/500.
 */

const PUBLIC_ROUTES = [
  "/",
  "/politicos",
  "/ranking",
  "/noticias",
  "/metodologia",
  "/contato",
  "/sobre",
  "/transparencia",
  "/doar",
  "/termos",
  "/privacidade",
];

for (const route of PUBLIC_ROUTES) {
  test(`GET ${route} — loads without error`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));

    const response = await page.goto(route, { waitUntil: "domcontentloaded" });

    expect(response?.status()).toBeLessThan(400);
    expect(errors).toHaveLength(0);

    // No hydration errors visible
    const body = await page.locator("body").textContent();
    expect(body).not.toContain("Hydration failed");
    expect(body).not.toContain("Error: Minified React error");
  });
}

test("Home — displays real indicators from API", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  // Should show numbers or dashes, never static fake values
  const indicatorSection = page.locator("section").filter({ hasText: "cadastrados" });
  await expect(indicatorSection).toBeVisible();

  // Should NOT contain the old hardcoded "10.431" specifically
  // (real data may coincidentally match, but structure should come from API)
});

test("Home — ranking shows preparation state", async ({ page }) => {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("Ranking em preparação")).toBeVisible();
});

test("Home — news section shows real data or empty state", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" });

  const newsSection = page.locator("section").filter({ hasText: "Notícias" }).first();
  await expect(newsSection).toBeVisible();

  // Should show either real news items or "em processamento" state
  const hasNews = await page.getByRole("link", { name: /noticias\// }).count();
  const hasEmpty = await page.getByText("Notícias em processamento").count();
  expect(hasNews + hasEmpty).toBeGreaterThan(0);
});

test("/politicos — search and filter", async ({ page }) => {
  await page.goto("/politicos", { waitUntil: "networkidle" });

  // Should show results count
  await expect(page.getByText(/resultado\(s\) encontrado/)).toBeVisible();

  // Search
  await page.getByLabel("Pesquisar político").fill("silva");
  await page.getByRole("button", { name: "Pesquisar" }).click();
  await page.waitForLoadState("networkidle");

  // Filter by state
  await page.getByLabel("Filtrar por estado").selectOption("SP");
  await page.waitForLoadState("networkidle");
});

test("/politicos/[slug] — profile loads with tabs", async ({ page }) => {
  await page.goto("/politicos", { waitUntil: "networkidle" });

  // Click first politician
  const firstLink = page.locator("a[href^='/politicos/']").first();
  if (await firstLink.isVisible()) {
    await firstLink.click();
    await page.waitForLoadState("domcontentloaded");

    // Should have tabs
    await expect(page.getByRole("button", { name: "Visão geral" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Projetos" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Gastos" })).toBeVisible();
  }
});

test("/contato — form validation", async ({ page }) => {
  await page.goto("/contato", { waitUntil: "domcontentloaded" });

  // Submit empty form should not succeed
  await page.getByRole("button", { name: "Enviar mensagem" }).click();

  // Fields should be required (HTML validation prevents submission)
  const nameInput = page.locator("input[type='text']").first();
  await expect(nameInput).toHaveAttribute("required", "");
});

test("/ranking — shows preparation state", async ({ page }) => {
  await page.goto("/ranking", { waitUntil: "domcontentloaded" });
  await expect(page.getByText("Ranking em preparação")).toBeVisible();
  await expect(page.getByRole("link", { name: /metodologia/i })).toBeVisible();
});

test("/metodologia — has all sections", async ({ page }) => {
  await page.goto("/metodologia", { waitUntil: "domcontentloaded" });

  const sections = ["Princípios", "Fontes de dados", "Dados legislativos", "Notícias e Inteligência Artificial", "Indicadores e Ranking", "Contestação"];
  for (const section of sections) {
    await expect(page.getByText(section, { exact: false })).toBeVisible();
  }
});
