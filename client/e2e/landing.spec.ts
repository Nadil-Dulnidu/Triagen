import { test, expect } from "@playwright/test";

test.describe("PullSense Landing Page", () => {
  test("should render the landing page hero, branding, and agent cards", async ({ page }) => {
    await page.goto("/");

    // Verify title and brand name
    await expect(page).toHaveTitle(/PullSense/);
    await expect(page.getByText("PullSense", { exact: false })).toBeVisible();

    // Verify hero tagline
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      "Autonomous Pull Request Reviews"
    );

    // Verify 6 agent feature cards
    await expect(page.getByText("Security Agent")).toBeVisible();
    await expect(page.getByText("Style & Clean Code Agent")).toBeVisible();
    await expect(page.getByText("Test Coverage Agent")).toBeVisible();
    await expect(page.getByText("Codebase Context Agent")).toBeVisible();
    await expect(page.getByText("Triage Agent")).toBeVisible();
    await expect(page.getByText("Aggregator Agent")).toBeVisible();
  });

  test("should have links to sign-in and sign-up", async ({ page }) => {
    await page.goto("/");

    const signInLink = page.getByRole("link", { name: "Sign In" });
    await expect(signInLink).toBeVisible();
    await expect(signInLink).toHaveAttribute("href", "/sign-in");

    const getStartedLink = page.getByRole("link", { name: "Get Started" });
    await expect(getStartedLink).toBeVisible();
    await expect(getStartedLink).toHaveAttribute("href", "/sign-up");
  });
});
