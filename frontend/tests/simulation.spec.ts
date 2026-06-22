import { expect, test } from "@playwright/test";

test("user can see simulation shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("AI 南大")).toBeVisible();
  await expect(page.getByRole("button", { name: /初始化/ })).toBeVisible();
});

test("user can initialize, step, select an agent, and submit an intervention", async ({
  page,
}) => {
  await page.goto("/");

  await page.getByRole("button", { name: /初始化/ }).click();

  await expect(page.getByText("8 locations")).toBeVisible();
  await expect(page.getByRole("button", { name: /王一诺/ })).toBeVisible();
  await expect(page.getByText("AI 南大的一周模拟开始了")).toBeVisible();
  await expect(page.locator(".timeBox")).toContainText("Day 1 07:30");

  await page.getByRole("button", { name: "单步" }).click();
  await expect(page.locator(".timeBox")).toContainText("Day 1 08:00");

  await page.getByRole("button", { name: /王一诺/ }).click();
  await expect(page.getByRole("heading", { name: "王一诺" })).toBeVisible();

  await page.getByPlaceholder("例如：你可以去社团招新点看看。").fill("你可以去社团招新点看看。");
  await page.getByRole("button", { name: "写入记忆" }).click();

  await expect(page.getByText("用户给王一诺留下建议")).toBeVisible();
});
