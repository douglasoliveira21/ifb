import { test, expect } from "@playwright/test";

/**
 * Admin News review flow tests.
 * Requires E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD.
 */

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || "";
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || "";

test.describe("Admin News Review", () => {
  test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, "E2E credentials not set");

  test.beforeEach(async ({ page }) => {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const response = await page.request.post(`${backendUrl}/api/v1/auth/login`, {
      data: { email: ADMIN_EMAIL, password: ADMIN_PASSWORD },
    });
    expect(response.ok()).toBeTruthy();
    const cookies = response.headers()["set-cookie"];
    if (cookies) {
      const url = new URL(backendUrl);
      await page.context().addCookies(
        cookies.split(",").map((c) => {
          const [nameVal] = c.trim().split(";");
          const [name, ...valParts] = nameVal.split("=");
          return { name: name.trim(), value: valParts.join("="), domain: url.hostname, path: "/" };
        })
      );
    }
  });

  test("Review queue shows pending items or empty state", async ({ page }) => {
    await page.goto("/admin/noticias", { waitUntil: "networkidle" });

    const hasItems = await page.locator("table tbody tr").count();
    const hasEmpty = await page.getByText("Nenhuma notícia aguardando revisão").count();

    expect(hasItems + hasEmpty).toBeGreaterThan(0);
  });

  test("Clicking a row opens detail drawer", async ({ page }) => {
    await page.goto("/admin/noticias", { waitUntil: "networkidle" });

    const firstRow = page.locator("table tbody tr").first();
    if (await firstRow.isVisible()) {
      await firstRow.click();
      // Drawer should open with classification details
      await expect(page.getByText("Categoria")).toBeVisible();
      await expect(page.getByText("Confiança")).toBeVisible();
    }
  });

  test("Approve button shows confirmation dialog", async ({ page }) => {
    await page.goto("/admin/noticias", { waitUntil: "networkidle" });

    const approveBtn = page.getByRole("button", { name: "Aprovar" }).first();
    if (await approveBtn.isVisible()) {
      await approveBtn.click();
      await expect(page.getByText("Aprovar classificação?")).toBeVisible();
      // Cancel instead of actually approving real data
      await page.getByRole("button", { name: "Cancelar" }).click();
    }
  });

  test("Reject button shows confirmation dialog", async ({ page }) => {
    await page.goto("/admin/noticias", { waitUntil: "networkidle" });

    const rejectBtn = page.getByRole("button", { name: "Rejeitar" }).first();
    if (await rejectBtn.isVisible()) {
      await rejectBtn.click();
      await expect(page.getByText("Rejeitar classificação?")).toBeVisible();
      await page.getByRole("button", { name: "Cancelar" }).click();
    }
  });
});
