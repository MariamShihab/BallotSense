# Accessibility pass — 2026-07-12

Scope: local MVP voter research flow covering contest selection, issue-lens
selection, cited brief rendering, source-proof disclosure, correction-report
submission, evidence-gap display, and private local note controls.

## What changed

- Added Playwright + axe coverage for the main cited-research and correction
  workflow.
- Added semantic `fieldset` grouping for contest radio buttons and issue-lens
  checkboxes.
- Added visible keyboard focus treatment for primary controls, links, summary
  disclosures, form fields, and local-note controls.
- Added live-region/status treatment for selected lenses, API errors, and
  correction-report feedback.
- Added screen-reader status wording for finding statuses such as `supported`
  and `insufficient_evidence`.

## Verification

- `npm --prefix web run test:a11y`
- `make check`

Both passed on 2026-07-12. The local Node runtime still prints the existing
React Router version warning because it is `v22.21.0` and React Router requests
`>22.22.0`; the build and tests completed successfully.

## Remaining manual review

This automated pass does not replace real tester sessions. Before broad demo
acceptance, still perform a manual keyboard-only walkthrough, a 200% zoom check,
and at least 3 real tester sessions focused on comprehension and trust.
