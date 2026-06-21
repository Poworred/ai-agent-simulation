import { expect, test } from "@playwright/test";

test("user can see simulation shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("AI 南大")).toBeVisible();
  await expect(page.getByRole("button", { name: /初始化/ })).toBeVisible();
});
