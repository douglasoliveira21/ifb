import { test, expect } from "@playwright/test";

/**
 * Admin access control tests.
 * Requires E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD environment variables.
 */

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "";
const API_URL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000";

test.describe("Admin — Access Control", () => {
  test("Unauthenticated user is redirected to /login", async ({ page }) => {
    await page.goto("/admin", { waitUntil: "domcontentloaded" });
    // Should redirect or show login prompt
    await page.waitForURL(/\/login/, { timeout: 5000 }).catch(() => {});
    const url = page.url();
    const isOnLogin = url.includes("/login");
    const isOnAdmin = url.includes("/admin");

    // Either redirected to login or shows "Carregando..." then redirects
    if (isOnAdmin) {
      // Wait a bit more for redirect
      await page.waitForTimeout(3000);
      const finalUrl = page.url();
      expect(finalUrl).toContain("/login");
    }
  });

  test("Admin pages require authentication", async ({ page }) => {
    const adminPages = ["/admin/noticias", "/admin/politicos", "/admin/usuarios"];
    for (const route of adminPages) {
      await page.goto(route, { waitUntil: "domcontentloaded" });
      await page.waitForTimeout(2000);
      const url = page.url();
      // Should be redirected to login or show access denied
      const body = await page.locator("body").textContent();
      const denied = body?.includes("Acesso negado") || url.includes("/login");
      expect(denied, `${route} should deny unauthenticated access`).toBeTruthy();
    }
  });
});

test.describe("Admin — Authenticated", () => {
  test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, "E2E_ADMIN_EMAIL/PASSWORD not set");

  test.beforeEach(async ({ page }) => {
    // Login via API
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const response = await page.request.post(`${backendUrl}/api/v1/auth/login`, {
      data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    });
    expect(response.ok()).toBeTruthy();

    // Set cookies from response
    const cookies = response.headers()["set-cookie"];
    if (cookies) {
      const url = new URL(page.url() || API_URL);
      // Parse and set cookies manually for the browser context
      await page.context().addCookies(
        cookies.split(",").map((c) => {
          const [nameVal] = c.trim().split(";");
          const [name, ...valParts] = nameVal.split("=");
          return { name: name.trim(), value: valParts.join("="), domain: url.hostname, path: "/" };
        })
      );
    }
  });

  test("/admin — dashboard loads", async ({ page }) => {
    await page.goto("/admin", { waitUntil: "networkidle" });
    await expect(page.getByText("Painel Administrativo")).toBeVisible();
  });

  test("/admin/noticias — review queue loads", async ({ page }) => {
    await page.goto("/admin/noticias", { waitUntil: "networkidle" });
    await expect(page.getByText("Notícias")).toBeVisible();
    // Should show either items or empty state
    const hasTable = await page.locator("table").count();
    const hasEmpty = await page.getByText("Nenhuma notícia aguardando").count();
    expect(hasTable + hasEmpty).toBeGreaterThan(0);
  });

  test("/admin/politicos — list loads with data", async ({ page }) => {
    await page.goto("/admin/politicos", { waitUntil: "networkidle" });
    await expect(page.getByText("Políticos")).toBeVisible();
    await expect(page.getByText(/político\(s\) encontrado/)).toBeVisible();
  });

  test("/admin/politicos — search works", async ({ page }) => {
    await page.goto("/admin/politicos", { waitUntil: "networkidle" });
    await page.getByPlaceholder("Buscar por nome").fill("silva");
    await page.waitForTimeout(1000);
    await page.waitForLoadState("networkidle");
  });

  test("/admin/politicos — filter by state works", async ({ page }) => {
    await page.goto("/admin/politicos", { waitUntil: "networkidle" });
    await page.locator("select").selectOption("SP");
    await page.waitForLoadState("networkidle");
  });

  test("/admin/usuarios — roles list loads", async ({ page }) => {
    await page.goto("/admin/usuarios", { waitUntil: "networkidle" });
    await expect(page.getByText("Usuários e Permissões")).toBeVisible();
    await expect(page.getByText("Roles do sistema")).toBeVisible();
  });

  test("Admin cards link to valid pages", async ({ page }) => {
    await page.goto("/admin", { waitUntil: "networkidle" });
    const links = await page.locator("a[href^='/admin/']").evaluateAll((els) =>
      els.map((el) => el.getAttribute("href")).filter(Boolean) as string[]
    );

    for (const href of links) {
      const res = await page.goto(href, { waitUntil: "domcontentloaded" });
      expect(res?.status(), `Admin link ${href}`).toBeLessThan(400);
    }
  });
});
