# BallotSense execution plan

This is the execution companion to the [system design and delivery
roadmap](system-design-and-roadmap.md) and the [source and citation
policy](source-policy.md). It converts their phases into the exact order of
work, concrete substeps, accountable roles, and a realistic timeline.

## How to use this plan

- Complete phases in order. Do not start a dependent phase because its UI or AI
  demo seems exciting.
- A phase is complete only when its **exit criteria** pass.
- The **Product owner** makes scope, source-policy, and release decisions.
- The **Engineering team** implements, tests, and documents the system.
- The **Corpus reviewer** approves election material before it enters
  retrieval. The product owner can fill this role for the early demo, but the
  review action must be recorded.

## Planning assumptions

- Start date: **Monday, July 13, 2026**.
- Scope: archived June 2026 California primary, beginning with one ballot
  measure and then one candidate race in Santa Clara County or an agreed
  nearby jurisdiction.
- Capacity: one developer with roughly 10–15 focused hours each week.
- First goal: a credible private/archive demo, not a rushed live-election app.
- November 3, 2026 is a possible later release target, subject to the launch
  gate in Phase 9.

If available capacity is higher or lower, preserve the order and exit criteria;
adjust dates rather than skipping safeguards.

## Timeline at a glance

| Weeks | Dates | Phase | Milestone |
| --- | --- | --- | --- |
| 1 | Jul 13–19 | 0 | Approved MVP scope and source plan |
| 2 | Jul 20–26 | 1 | Repeatable local development foundation |
| 3–4 | Jul 27–Aug 9 | 2 | First reviewed election corpus |
| 5–6 | Aug 10–23 | 3 | Firestore retrieval returns approved evidence only |
| 7–8 | Aug 24–Sep 6 | 4 | Cited generation with enforced validation |
| 9–10 | Sep 7–20 | 5 | Usable, mobile archive-demo research UI |
| 11 | Sep 21–27 | 6 | End-to-end archive demo and user feedback |
| 12–13 | Sep 28–Oct 11 | 7 | Quality, privacy, security, and deployment hardening |
| 14–16 | Oct 12–Nov 1 | 8–9 | Optional November corpus/release decision; OCR only if already safe |

## Phase 0 — Lock the product contract

**Dates:** Jul 13–19  
**Outcome:** Everyone agrees on what BallotSense will do for the first demo and
what it will explicitly not do.

### 0.1 Product-owner decisions

- [ ] Confirm the initial product promise: cited research assistance, not a
  voting recommendation.
- [ ] Confirm that the MVP has no numeric candidate match score.
- [ ] Confirm that the MVP has no free-text values input and no durable voter
  profile.
- [ ] Confirm the selected issue lenses. Recommended initial set:
  housing affordability, public safety, climate/environment, and public
  education.
- [ ] Choose the first **one ballot measure** for the initial vertical slice.
- [ ] Choose the first **one candidate race** to add after the measure works.
- [ ] Name the person responsible for source approval and corrections.
- [ ] Approve the privacy statement: ballot images, addresses, preferences, and
  choices are not stored by default.

### 0.2 Engineering and corpus setup

- [ ] Create an `election-scope` record: election ID, date, jurisdictions,
  supported contests, and current corpus version.
- [ ] Create a source inventory spreadsheet or internal table for the first
  measure: title, URL, publisher, source type, date, expected pages/sections,
  reviewer, and status.
- [ ] Identify only allowed initial sources: official measure text, county/state
  voter guide, and elections-office material.
- [ ] Write the voter-facing non-endorsement and uncertainty copy.
- [ ] Create the initial correction-report template.

### Phase 0 exit criteria

- [ ] The first measure and race are named.
- [ ] The issue-lens list is approved.
- [ ] Every planned source has an owner and review state.
- [ ] The product owner agrees that unsupported claims return “No verified
  information found.”

**Do not proceed if:** the team has not selected a first measure/source set. Do
not start model prompts, OCR, or a broad UI before this decision.

## Phase 1 — Establish the local engineering foundation

**Dates:** Jul 20–26  
**Outcome:** The repository can safely run, test, and validate core contracts
on a developer machine.

### 1.1 Repository and environment

- [x] Add source, source-chunk, citation, and claim data contracts.
- [x] Add a minimal FastAPI application and source-catalog interface.
- [x] Add source policy and system design documents.
- [x] Add baseline tests that fail a claim without citations and an approved
  source without a review timestamp.
- [ ] Add a Remix application skeleton and Tailwind setup.
- [ ] Add `.env.example` files with variable names only—never real credentials.
- [ ] Add formatting/lint commands for Python and TypeScript.
- [ ] Add a single local startup command or documented two-service startup
  flow.
- [ ] Add CI to run formatting, contract tests, and unit tests on each pull
  request.

### 1.2 Contract hardening

- [ ] Add IDs and schemas for elections, contests, candidates, measures,
  source chunks, and review actions.
- [ ] Add explicit `insufficient_evidence` response schema.
- [ ] Add a response validator that rejects recommendation language and a claim
  without citations.
- [ ] Add synthetic fixtures clearly marked as non-election data.

### 1.3 Verify

- [ ] Create a clean local virtual environment.
- [ ] Install declared development dependencies.
- [ ] Run the full test suite.
- [ ] Check that no secret, ballot image, or real voter data is tracked.

### Phase 1 exit criteria

- [ ] A developer can follow the README to run API tests successfully.
- [ ] The test suite includes the cited-claim and source-review invariants.
- [ ] The local repository contains no election claim presented as fact without
  a source record.

**Current status:** Partially complete. The Python contracts, API scaffold, and
four baseline tests exist; the frontend, CI, expanded schemas, and validator
are still pending.

## Phase 2 — Build the first reviewed source corpus

**Dates:** Jul 27–Aug 9  
**Outcome:** One measure has an auditable, human-approved set of source chunks.

### 2.1 Acquire and version source documents

For the selected measure:

- [ ] Find the canonical official measure text.
- [ ] Find the official voter-guide explanation and relevant county/state
  election material.
- [ ] Record source URL, publisher, source type, publication date, retrieval
  date, election ID, jurisdiction, and measure ID.
- [ ] Download or snapshot permitted source artifacts to the planned protected
  artifact store.
- [ ] Compute and record a SHA-256 content hash.
- [ ] Mark every source `pending`; no material is searchable yet.

### 2.2 Extract and prepare chunks

- [ ] Extract the source text; record extraction method and tool version.
- [ ] Correct obvious extraction errors only against the source document.
- [ ] Split content into coherent chunks that preserve context and attribution.
- [ ] Attach page number, section heading, and source ID to every chunk.
- [ ] Map each chunk to the selected measure and election.
- [ ] Identify chunks supporting: what changes, implementation/authority,
  funding/cost language, and official arguments where available.

### 2.3 Human review

- [ ] Check the document is authentic and belongs to the selected election.
- [ ] Check every chunk’s text against its source page/section.
- [ ] Check locators work and chunks do not omit material qualifying language.
- [ ] Record reviewer, timestamp, decision, and notes.
- [ ] Mark approved chunks `approved_for_retrieval`; quarantine rejected or
  uncertain chunks.
- [ ] Add at least one intentional evidence gap to test abstention behavior.

### Phase 2 exit criteria

- [ ] Every approved chunk opens a source artifact and locator.
- [ ] The first measure has enough approved material for a factual summary.
- [ ] The reviewer can reproduce what was approved and why.
- [ ] No pending/rejected source is eligible for retrieval.

**Do not proceed if:** sources are incomplete, have no stable locator, or no
human review record. More model tuning cannot compensate for this.

## Phase 3 — Provision persistent data and retrieval

**Dates:** Aug 10–23  
**Outcome:** The backend finds only relevant, approved evidence for a selected
contest and issue lens.

### 3.1 GCP and Firestore setup

- [ ] Create separate development and staging GCP configuration.
- [ ] Create Firestore in Native mode.
- [ ] Define collections for elections, contests, measures, sources,
  source-chunks, ingestion runs, and claim audits.
- [ ] Create a protected Cloud Storage bucket for immutable permitted source
  snapshots.
- [ ] Configure least-privilege service accounts and Secret Manager bindings.
- [ ] Add Firestore indexes, including native vector indexes using **cosine
  similarity** for approved source chunks.

### 3.2 Ingestion implementation

- [ ] Replace the empty in-memory source repository with a Firestore
  repository behind the same API contract.
- [ ] Build a non-public ingestion command or Cloud Run Job.
- [ ] Store source records and chunks with their review state.
- [ ] Generate embeddings only after review approval.
- [ ] Store embedding-model version beside each vector.
- [ ] Record the ingestion run, errors, and corpus version.

### 3.3 Retrieval implementation

- [ ] Implement metadata filtering: exact election ID, contest/measure ID,
  approved review state, and source-tier rules.
- [ ] Implement native Firestore cosine vector search for each selected lens.
- [ ] Deduplicate near-identical chunks and keep source diversity where
  possible.
- [ ] Return source ID, chunk ID, source type, date, locator, and verbatim text
  in the evidence packet.
- [ ] Return an empty evidence packet safely when nothing is approved.

### 3.4 Verify

- [ ] Test that a relevant measure query retrieves expected approved chunks.
- [ ] Test that a source from another election or contest cannot be retrieved.
- [ ] Test that pending/rejected chunks cannot be retrieved.
- [ ] Test that no source locator is lost in retrieval.

### Phase 3 exit criteria

- [ ] Retrieval operates against Firestore, not mock data.
- [ ] Every returned chunk is approved, contest-bound, and linkable.
- [ ] Empty or weak evidence produces a safe empty result rather than a broad
  search across unrelated material.

## Phase 4 — Add constrained AI generation and validation

**Dates:** Aug 24–Sep 6  
**Outcome:** The system can turn an approved evidence packet into a short,
cited measure brief—or safely decline to do so.

### 4.1 Define the answer shape before prompting

- [ ] Define JSON schemas for summary claims, claim category, citations,
  attribution, evidence gaps, and source cards.
- [ ] Define allowed measure-brief sections: `what_changes`,
  `who_implements`, `funding_or_authority`, `what_is_uncertain`, and
  `official_arguments` when sources support them.
- [ ] Define prohibited output: endorsement, candidate ranking, unsupported
  forecast, party-based inference, and numeric match score.

### 4.2 Gemini integration

- [ ] Store Gemini credentials in Secret Manager.
- [ ] Send Gemini only the selected evidence packet and structured lenses.
- [ ] Require it to use only supplied text, never baseline knowledge.
- [ ] Require strict JSON and citation of supplied chunk IDs.
- [ ] Require `insufficient_evidence` when sources do not support an answer.

### 4.3 Deterministic validation

- [ ] Validate every citation exists in the current evidence packet.
- [ ] Validate cited chunks are approved and bound to the requested contest.
- [ ] Validate every factual claim has at least one citation.
- [ ] Validate candidate/campaign claims have required attribution.
- [ ] Detect/reject prohibited recommendation and score fields.
- [ ] On invalid output, retry once with corrective instructions or return the
  safe abstention state.
- [ ] Write a redacted claim audit record with corpus version and validator
  outcome.

### 4.4 Evaluation

- [ ] Create 15–25 reviewed test questions: straightforward facts, ambiguous
  text, missing information, and false-premise requests.
- [ ] Manually grade whether each claim is actually supported by its citation.
- [ ] Measure citation validity, citation support, abstention quality, and
  prohibited-output rate.
- [ ] Fix retrieval, schemas, or prompt rules before expanding scope.

### Phase 4 exit criteria

- [ ] A measure brief returns only validated cited claims.
- [ ] Invalid/uncited responses cannot reach the API caller.
- [ ] Evidence gaps visibly return an insufficient-evidence result.
- [ ] Human evaluation finds no unsupported display claim in the acceptance set.

**Do not proceed if:** a citation can point to the wrong chunk or a claim can
reach the UI without evidence.

## Phase 5 — Build the voter research experience

**Dates:** Sep 7–20  
**Outcome:** A voter can understand one measure in a few minutes and inspect
every supporting source on a phone.

### 5.1 Build the first screen flow

- [ ] Create a welcome screen with the trust promise and non-endorsement
  language.
- [ ] Create structured issue-lens selection, limited to the approved list.
- [ ] Create a supported-contest picker containing the first measure.
- [ ] Call the cited-brief API after the user confirms their selection.
- [ ] Render clear loading, error, no-coverage, and insufficient-evidence
  states.

### 5.2 Build the evidence-first measure brief

- [ ] Show what the measure changes before analysis.
- [ ] Show short claims with visible source-type and date badges.
- [ ] Add `Show the proof` on every factual claim.
- [ ] Render the citation’s publisher, title, locator, excerpt, and canonical
  link.
- [ ] Clearly label official facts versus arguments attributed to proponents or
  opponents.
- [ ] Add a correction-report link tied to the claim/source ID.

### 5.3 Privacy and accessibility

- [ ] Keep lenses and temporary navigation state in browser session memory.
- [ ] Do not add accounts, backend notes, address storage, or ballot upload.
- [ ] Add a clear-local-data control if local notes/bookmarks exist.
- [ ] Test keyboard navigation, focus order, contrast, headings, and screen
  reader source descriptions.
- [ ] Test phone layouts at common narrow widths.

### Phase 5 exit criteria

- [ ] A voter can reach the full source from every displayed claim.
- [ ] A voter can tell the difference between a factual source and a campaign
  statement.
- [ ] No source gap looks like a negative judgment about a candidate or measure.
- [ ] The experience works without an account or ballot upload.

## Phase 6 — Add one candidate race

**Dates:** Sep 21–27  
**Outcome:** The product proves it can make a symmetric, attributed comparison
without making a recommendation.

### 6.1 Corpus expansion

- [ ] Identify the selected candidate race and official ballot labels.
- [ ] Gather official candidate statements first, then permitted campaign
  statements if needed.
- [ ] Apply the same search, chunking, and review process to every candidate.
- [ ] Record source coverage for each candidate and lens.
- [ ] Mark missing information as a gap, not a position.

### 6.2 Comparison flow

- [ ] Add a candidate comparison view for selected lenses.
- [ ] Build the evidence-coverage table with source-type labels.
- [ ] Attribute all candidate/campaign claims in visible text.
- [ ] Prohibit candidate order from implying a ranking; use ballot order or
  neutral alphabetical order consistently.
- [ ] Add explicit “No verified position found” cards.

### 6.3 Verify

- [ ] Test equivalent retrieval workflows for every candidate.
- [ ] Test that one candidate’s sources never support another’s claim.
- [ ] Test the UI on sparse coverage and unequal source availability.
- [ ] Ask a reviewer whether a user could mistake the comparison for an
  endorsement.

### Phase 6 exit criteria

- [ ] All candidate statements are attributed and cited.
- [ ] Missing evidence is visible and neutral.
- [ ] The app contains no numerical alignment score or “best candidate” output.

## Phase 7 — End-to-end archive demo and quality hardening

**Dates:** Sep 28–Oct 11  
**Outcome:** A limited, end-to-end demo is reliable enough for outside feedback.

### 7.1 End-to-end checks

- [ ] Run the entire measure and candidate flows using staging data.
- [ ] Test every source link, citation locator, and error state.
- [ ] Test source version changes and correction workflow.
- [ ] Test blank corpus, model timeout, invalid JSON, and Firestore outage
  behavior.
- [ ] Confirm graceful failure returns a transparent unavailable state.

### 7.2 Privacy and security review

- [ ] Verify logs do not contain voters’ lenses, addresses, notes, prompts, or
  ballot bytes.
- [ ] Verify service-account permissions are least privilege.
- [ ] Verify secrets are absent from Git and runtime responses.
- [ ] Configure CORS, HTTPS, content security policy, input limits, rate
  limiting, and error handling.
- [ ] Perform a dependency and vulnerability scan.

### 7.3 Usability sessions

- [ ] Recruit 5–8 test voters.
- [ ] Ask them to explain a measure using the app.
- [ ] Ask them to find the proof behind a claim.
- [ ] Ask them what “No verified position found” means.
- [ ] Record confusion points and correct wording/interaction issues.

### Phase 7 exit criteria

- [ ] No critical privacy, security, or citation issue remains open.
- [ ] Test voters understand that BallotSense is a research tool, not a
  recommender.
- [ ] Staging deployment, monitoring, and rollback are documented and tested.

## Phase 8 — Deploy the archive demo

**Dates:** Oct 12–18  
**Outcome:** The completed June archive demo is available to the intended
audience with clear limitations.

### 8.1 Deployment

- [ ] Containerize frontend and API separately.
- [ ] Deploy staging and production Cloud Run services from immutable images.
- [ ] Configure Firestore, Cloud Storage, Secret Manager, custom domain, and
  monitoring.
- [ ] Set Cloud Run scaling limits and GCP budget alerts.
- [ ] Create a public status/contact route and correction-report process.

### 8.2 Release checklist

- [ ] Label the experience clearly as an archived June 2026 demo.
- [ ] Publish the source policy, privacy statement, and limitations.
- [ ] Record active code revision and corpus version.
- [ ] Confirm rollback to a prior Cloud Run revision/corpus version.
- [ ] Test production smoke flow without sending real voter personal data.

### Phase 8 exit criteria

- [ ] Archive demo is public or available to its intended reviewers.
- [ ] Observability, correction ownership, and rollback work.
- [ ] The release makes no claim to cover a current live ballot.

## Phase 9 — Decide whether to support November 2026

**Dates:** Oct 19–Nov 1  
**Outcome:** A deliberate go/no-go decision, based on evidence readiness rather
than calendar pressure.

### 9.1 Prepare a potential November corpus

- [ ] Confirm official election dates, candidate lists, ballot measures, and
  voter-guide availability.
- [ ] Create a coverage matrix: every planned contest × every candidate/measure
  × available reviewed sources.
- [ ] Acquire, hash, extract, and review November sources under the same policy.
- [ ] Rerun retrieval and generation evaluation for the November corpus.

### 9.2 Make the go/no-go decision

Publish a current-election experience only when all statements are true:

- [ ] Every displayed contest meets the defined minimum coverage standard.
- [ ] Citation validity/support evaluation passes the agreed threshold.
- [ ] Candidate comparisons use symmetric workflow and clear attribution.
- [ ] Privacy/security review remains clean.
- [ ] Monitoring, correction response, cost limits, and rollback have a named
  owner.

If any box is unchecked, keep the archive demo and do **not** rush a live
release.

## Optional Phase 10 — Ballot discovery and OCR

**Start only after Phase 8 is stable.**  
**Target date:** After archive-demo acceptance; it is not a launch dependency.

### 10.1 Address-based discovery first

- [ ] Decide whether address resolution can use a trusted official/approved
  dataset without retaining full addresses.
- [ ] Resolve address to districts/contests ephemerally.
- [ ] Show the inferred ballot and require confirmation.
- [ ] Add manual contest selection as a permanent fallback.

### 10.2 OCR second

- [ ] Display instruction to use an unmarked ballot or official sample ballot.
- [ ] Add in-memory file type, size, and request validation.
- [ ] Send images only to the isolated OCR request flow.
- [ ] Extract contest labels/candidates only; do not detect selections.
- [ ] Immediately discard image buffers after response or error.
- [ ] Require the voter to confirm/correct every contest before research.
- [ ] Verify logs, error reporting, and caches contain no image bytes.
- [ ] Add a feature flag so OCR can be disabled immediately.

### Phase 10 exit criteria

- [ ] OCR errors cannot silently produce a wrong contest list.
- [ ] Automated tests demonstrate no image persistence.
- [ ] The core guide works fully when OCR is disabled.

## Weekly working rhythm

Use this repeatable rhythm for every active phase:

| Day | Activity |
| --- | --- |
| Monday | Confirm the week’s checklist, dependencies, owner, and definition of done. |
| Tuesday–Thursday | Build only the current phase’s deliverables; add tests as work is added. |
| Friday | Run the phase checks, demo the result, record decisions, and update the checklist. |
| Before next phase | Confirm exit criteria with the product owner; log deferred work rather than carrying hidden risk forward. |

## First-week checklist: what to do now

The immediate next actions are intentionally simple:

1. **Product owner:** Reply with the first archived ballot measure you want to
   use, or authorize research to select the best-supported official measure.
2. **Product owner:** Approve or revise these lenses: housing affordability,
   public safety, climate/environment, public education.
3. **Product owner:** Confirm whether you will serve as the first corpus
   reviewer.
4. **Engineering:** Create the source inventory for that measure and find the
   official primary sources.
5. **Engineering:** Record sources as `pending`; do not build AI answers yet.
6. **Product owner + reviewer:** Approve the first source/chunk set.

After those six steps, Phase 2 begins with real, verifiable material.

## Scope-protection rules

When time is limited, cut in this order:

1. Cut OCR.
2. Cut address lookup.
3. Cut free-text values.
4. Cut broad contest/geography coverage.
5. Keep citation enforcement, human source review, uncertainty states, and
   privacy protections.

Never cut the controls that make the product trustworthy in order to add a more
impressive-looking AI feature.
