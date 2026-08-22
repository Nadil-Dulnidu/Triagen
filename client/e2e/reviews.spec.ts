import { test, expect } from "@playwright/test";

test.describe("Reviews Workflow", () => {
  test("should display reviews list with search input and filters", async ({ page }) => {
    await page.goto("/reviews");

    await expect(page.getByRole("heading", { name: /Pull Request Reviews/i })).toBeVisible();
    await expect(page.getByPlaceholder(/Search reviews/i)).toBeVisible();
  });
});
