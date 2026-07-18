# BallotSense demo readiness checklist

Use this checklist before showing BallotSense to someone else.

## 1. Public repo check

- [ ] Latest GitHub Actions run on `main` is green.
- [ ] GitHub README renders clearly.
- [ ] CI badge is visible.
- [ ] SVG wireframe/mockup is visible.
- [ ] Mermaid architecture and product-flow diagrams render.
- [ ] README accurately says the archive demo does not upload ballot images or
  run OCR.

## 2. Local server check

- [ ] Web app opens locally.
- [ ] API docs open locally.
- [ ] `POST /api/v1/briefs` returns a supported Measure D finding.
- [ ] `POST /api/v1/briefs` returns an `insufficient_evidence` finding for a
  lens with no reviewed source support.
- [ ] Correction report submission returns a reviewer-follow-up message.

Suggested local URLs:

- Web: `http://127.0.0.1:5174/` when running the fixture smoke-test setup.
- API docs: `http://127.0.0.1:8001/docs` when running the fixture smoke-test
  setup.

## 3. UI walkthrough

- [ ] Hero clearly says this is an archived June 2026 demo.
- [ ] The page clearly says the demo is Measure D only.
- [ ] Board of Supervisors District 1 is visibly marked as not covered yet.
- [ ] User can select up to three issue lenses.
- [ ] `View cited research` displays reviewed Measure D research.
- [ ] Supported finding card shows a cited-evidence status.
- [ ] Insufficient-evidence card looks intentional, not broken.
- [ ] Source-proof disclosure says `Inspect source proof for this claim`.
- [ ] Original source link opens the official source in a new tab.
- [ ] Correction form warns users not to include vote choice, address, email,
  phone number, or private notes.
- [ ] Private session note remains local-only.

## 4. Trust and safety language

- [ ] The demo says BallotSense is research assistance, not a recommendation.
- [ ] The demo says it does not rank choices or show a match score.
- [ ] The demo says ballot upload/OCR is intentionally omitted.
- [ ] The demo says no account or durable voter profile is stored.
- [ ] Official lookup links are labeled as external county tools.

## 5. November 2026 source readiness

- [ ] Run `make check-november-sources`.
- [ ] If the official voter-guide package is still unpublished, do not snapshot,
  ingest, embed, or display Prop 1 / Prop 45 voter-facing answers.
- [ ] If the official voter-guide package is published, begin the source review
  process before any retrieval or generation work.

## 6. Pre-demo script

Suggested walkthrough:

1. "BallotSense is not telling you how to vote; it is showing reviewed evidence."
2. Pick Measure D.
3. Select `Climate/environment` and `Public education`.
4. Click `View cited research`.
5. Point out that one card has cited evidence.
6. Point out that one card abstains because the corpus lacks verified evidence.
7. Open `Inspect source proof for this claim`.
8. Show the official source link.
9. Open the correction form and explain reviewer follow-up.
10. Close by showing the README and explaining that November 2026 sources are
    monitored but not ingested until official voter-guide materials are
    published.

## Current checked state

Last verified during this pass:

- Latest GitHub Actions run for `Polish GitHub README`: green.
- GitHub README page: reachable and rendering README content, SVG mockup, and
  Mermaid enrichment.
- Local web page: reachable.
- Local cited-research route: returned one supported finding and one
  `insufficient_evidence` finding.
