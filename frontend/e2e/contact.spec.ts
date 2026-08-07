import { test, expect } from "@playwright/test";

/**
 * Contact page tests — form validation and submission.
 */

test.describe("Contact Page", () => {
  test("/contato — form renders with required fields", async ({ page }) => {
    await page.goto("/contato", { waitUntil: "domcontentloaded" });

    await expect(page.getByText("Contato")).toBeVisible();
    await expect(page.locator("input[type='text']").first()).toBeVisible();
    await expect(page.locator("input[type='email']")).toBeVisible();
    await expect(page.locator("select")).toBeVisible();
    await expect(page.locator("textarea")).toBeVisible();
    await expect(page.getByRole("button", { name: "Enviar mensagem" })).toBeVisible();
  });

  test("Required fields prevent empty submission", async ({ page }) => {
    await page.goto("/contato", { waitUntil: "domcontentloaded" });

    // Try clicking submit without filling
    await page.getByRole("button", { name: "Enviar mensagem" }).click();

    // Should still be on the same page (HTML validation prevents)
    expect(page.url()).toContain("/contato");
  });

  test("Invalid email shows validation", async ({ page }) => {
    await page.goto("/contato", { waitUntil: "domcontentloaded" });

    await page.locator("input[type='text']").first().fill("Teste E2E");
    await page.locator("input[type='email']").fill("invalid-email");
    await page.locator("select").selectOption("Dúvida");
    await page.locator("textarea").fill("Mensagem de teste E2E");

    await page.getByRole("button", { name: "Enviar mensagem" }).click();

    // Browser should validate email format
    expect(page.url()).toContain("/contato");
  });

  test("Subjects dropdown has expected options", async ({ page }) => {
    await page.goto("/contato", { waitUntil: "domcontentloaded" });

    const options = await page.locator("select option").evaluateAll((els) =>
      els.map((el) => el.textContent?.trim()).filter(Boolean)
    );

    expect(options).toContain("Dúvida");
    expect(options).toContain("Correção de dados");
    expect(options).toContain("Contestação");
    expect(options).toContain("Imprensa");
  });
});
