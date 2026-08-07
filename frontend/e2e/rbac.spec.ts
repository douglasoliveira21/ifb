import { test, expect } from "@playwright/test";

/**
 * RBAC validation — tests that the backend actually enforces permissions.
 * Uses direct API calls (not frontend-only).
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

test.describe("RBAC — Backend enforcement", () => {
  test("Unauthenticated request to admin endpoint returns 401", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/admin/news/review-queue`);
    expect(response.status()).toBe(401);
  });

  test("Unauthenticated request to user profile returns 401", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/users/me`);
    expect(response.status()).toBe(401);
  });

  test("Unauthenticated request to admin roles returns 401", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/v1/admin/roles`);
    expect(response.status()).toBe(401);
  });

  test("Public endpoints are accessible without auth", async ({ request }) => {
    const publicEndpoints = [
      "/api/v1/health",
      "/api/v1/stats",
      "/api/v1/politicians?limit=1",
      "/api/v1/news/latest?limit=1",
    ];

    for (const endpoint of publicEndpoints) {
      const response = await request.get(`${BACKEND_URL}${endpoint}`);
      expect(response.status(), `${endpoint} should be public`).toBeLessThan(400);
    }
  });

  test("Admin endpoints reject requests without proper role", async ({ request }) => {
    // This test verifies that even if someone reaches the endpoint,
    // the backend denies access based on JWT/role, not just frontend routing.
    const adminEndpoints = [
      { method: "GET", path: "/api/v1/admin/news/review-queue" },
      { method: "GET", path: "/api/v1/admin/roles" },
      { method: "GET", path: "/api/v1/admin/politicians" },
    ];

    for (const { method, path } of adminEndpoints) {
      const response = method === "GET"
        ? await request.get(`${BACKEND_URL}${path}`)
        : await request.post(`${BACKEND_URL}${path}`);
      // Should be 401 (no token) or 403 (wrong role)
      expect([401, 403]).toContain(response.status());
    }
  });
});
