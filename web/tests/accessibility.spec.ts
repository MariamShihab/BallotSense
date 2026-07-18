import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const briefResponse = {
  election_id: "ca-scc-2026-primary",
  contest_id: "scvosa-measure-d",
  disclaimer: "Research assistance only; BallotSense does not recommend or rank choices.",
  findings: [
    {
      status: "supported",
      lens_id: "climate-environment",
      summary: {
        text: "Measure D provides additional accountability measures for the tax proceeds.",
        citations: [
          {
            source_id: "scvosa-measure-d-impartial-analysis",
            chunk_id: "scvosa-measure-d-analysis-accountability",
            locator: "PDF p. 1, accountability paragraph",
            public_source_url: "https://example.gov/measure-d.pdf",
            source_type: "elections_office_material",
          },
        ],
      },
      explanation: null,
    },
    {
      status: "insufficient_evidence",
      lens_id: "public-education",
      summary: null,
      explanation: "BallotSense could not verify enough reviewed evidence for this lens.",
    },
  ],
};

test("main cited-research and correction flow has no obvious accessibility violations", async ({
  page,
}) => {
  await page.route("**/api/v1/briefs", async (route) => {
    await route.fulfill({ json: briefResponse });
  });
  await page.route("**/api/v1/corrections", async (route) => {
    const body = route.request().postDataJSON();
    expect(body).not.toHaveProperty("vote_choice");
    expect(body).not.toHaveProperty("local_note");
    await route.fulfill({
      json: {
        report_id: "c734c6ef-c425-45df-b467-9eb5ecbef493",
        status: "pending",
        message: "Correction report received for reviewer follow-up.",
      },
    });
  });

  await page.goto("/");

  const initialAccessibility = await new AxeBuilder({ page }).analyze();
  expect(initialAccessibility.violations).toEqual([]);

  await expect(page.getByRole("heading", { name: "Scan a ballot item" })).toBeVisible();
  await page.setInputFiles("#ballot-scanner-image", {
    name: "prop-36-sample-ballot.png",
    mimeType: "image/png",
    buffer: Buffer.from(
      "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
      "base64",
    ),
  });
  await expect(page.getByText("Image loaded in memory only")).toBeVisible();
  await page.getByRole("button", { name: "Confirm Proposition 36" }).click();
  await expect(page.getByText("Proposition 36 is confirmed")).toBeVisible();
  await page.getByLabel("Measure D").check();

  await page.getByRole("button", { name: "View cited research" }).click();
  await expect(page.getByRole("heading", { name: "What the reviewed material says" })).toBeVisible();
  await expect(page.getByText("Research assistance only")).toBeVisible();

  const summary = page.getByText("Inspect source proof");
  await summary.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Official elections material")).toBeVisible();

  await page.getByRole("button", { name: "Report an issue with this source" }).click();
  await expect(page.getByLabel("Issue type")).toBeVisible();
  await page.getByLabel("What should a reviewer check?").fill(
    "Please check whether this source proof matches the displayed summary.",
  );
  await page.getByRole("button", { name: "Submit correction report" }).click();
  await expect(page.getByText("Correction report received")).toBeVisible();

  const finalAccessibility = await new AxeBuilder({ page }).analyze();
  expect(finalAccessibility.violations).toEqual([]);
});
