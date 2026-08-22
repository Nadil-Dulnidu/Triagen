import { test, expect } from "@playwright/test";

test.describe("Dashboard Navigation & Pages", () => {
  test("should render the dashboard layout and primary navigation links", async ({ page }) => {
    await page.goto("/dashboard");

    // Check sidebar navigation items
    await expect(page.getByRole("link", { name: /Dashboard/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Reviews/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Repositories/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Team Memory/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /Analytics/i })).toBeVisible();
  });

  test("should navigate to Repositories and show GitHub App Guide trigger", async ({ page }) => {
    await page.goto("/repositories");

    await expect(page.getByRole("heading", { name: /Repositories/i })).toBeVisible();
    await expect(
      page.getByRole("button", { name: /GitHub App Setup Guide/i })
    ).toBeVisible();
  });

  test("should navigate to Team Memory dashboard", async ({ page }) => {
    await page.goto("/memory");

    await expect(page.getByRole("heading", { name: /Persistent Team Memory/i })).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Memory Rule/i })).toBeVisible();
  });

  test("should navigate to Analytics dashboard", async ({ page }) => {
    await page.goto("/analytics");

    await expect(page.getByRole("heading", { name: /Review Analytics/i })).toBeVisible();
    await expect(page.getByText("Total AI Reviews")).toBeVisible();
  });
});
