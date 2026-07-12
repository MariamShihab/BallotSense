# BallotSense AI execution playbook

## Purpose

This is the **strict execution order** for BallotSense. It converts the system
design into small tasks that an AI assistant can execute, verify, and report
back on.

Read this file together with:

- [System design and delivery roadmap](system-design-and-roadmap.md) — the
  architecture and product rationale.
- [Source and citation policy](source-policy.md) — the non-negotiable rules for
  election material and claims.

When the two documents seem to conflict, the source policy controls anything
about what may be used as evidence; the system design controls architecture and
product boundaries. This playbook controls **execution order**.

## How to use this playbook

### Timeline convention

`Week 0` begins on the day the product owner approves the Phase 0 decision
packet. Durations are planning targets, not permission to skip quality gates.
A phase does not finish when its time box ends; it finishes only when its
acceptance checklist passes.

The first realistic goal is a small, private **archived June 2026 demo** in
approximately 9–10 weeks. A public November release remains conditional on the
release gate in Phase 8; it is never automatic.

### Ownership key

| Owner | Meaning |
| --- | --- |
| **AI** | The AI assistant can do this directly in the repository or using approved project access. |
| **You** | A product, legal, factual-review, spending, or account-permission decision that only the project owner may make. |
| **Shared** | The AI prepares the work; you review and approve the result. |

### Rules for the AI before every task

1. Read `AGENTS.md`, this playbook, the system design, and the source policy if
   the task affects product behavior, source data, AI, privacy, security, or
   deployment.
2. Check the active Git branch and working-tree status; preserve unrelated
   user changes.
3. Work only on the current phase and its prerequisites. Do not build a later
   feature early because it seems easy.
4. Use synthetic fixtures until a human approves real source material.
5. Run the relevant tests or validation after each implementation unit.
6. Report what changed, what was verified, and any decision needed from you.
7. Never modify `.env` secrets, Firestore security rules, or `AGENTS.md`
   without explicit approval.
8. Never treat a model output, a campaign statement, or an unreviewed source as
   verified election fact.

### Global stop rules

The AI must stop and request direction when:

- a source is ambiguous, paywalled, altered, or not clearly permitted by the
  source policy;
- an action needs GCP billing, credentials, production access, a public
  deployment, or an external message;
- a task would require storing a ballot image, voter address, voter preference,
  or personal note;
- a generated claim lacks direct reviewed support; or
- the next task changes the agreed product boundary.

## Master timeline

| Weeks | Phase | Deliverable | Gate |
| --- | --- | --- | --- |
| 0–1 | 0. Product decisions | Signed MVP decision packet and source inventory | You approve scope and source policy application. |
| 1–2 | 1. Engineering foundation | Runnable API + React Router framework shell + CI-quality local checks | Citation contracts and tests pass. |
| 2–4 | 2. Curated corpus | Reviewed source/chunk set for one measure and one race | Every approved chunk has provenance and a locator. |
| 4–5 | 3. Firestore retrieval | Filtered cosine retrieval over approved chunks | Wrong-election and unapproved chunks cannot be returned. |
| 5–6 | 4. Cited generation | Validated contest-brief API and evaluation set | Unsupported claims are rejected or abstain. |
| 6–8 | 5. Research UI | Mobile cited research brief for the archive demo | Test voter can inspect proof for every claim. |
| 8–10 | 6. Demo review | Staging demo, usability findings, corrections | No high-severity citation or privacy issue remains. |
| 10–12 | 7. Optional ballot discovery | Address confirmation; OCR only if warranted | No ballot image persistence and user confirmation proven. |
| 12+ | 8. Public-election gate | Go/no-go decision for November or later | All release criteria pass; otherwise remain an archive demo. |

## Current execution status

Completed work is checked below. An unchecked item is intentionally not
complete, even if related setup work has begun.

- [x] **0.1** Created the MVP decision packet and recorded the initial demo
      boundary.
- [x] **0.2** Selected Measure D and Board of Supervisors, District 1 as the
      first two archive-demo contests.
- [x] **0.3** Selected four issue lenses: housing affordability, public safety,
      climate/environment, and public education.
- [x] **0.4** Assigned the project owner as source reviewer, backup reviewer,
      and correction owner.
- [x] **1.1** Created the API foundation, documented the repo structure, and
      added the `web/` React Router framework app with Tailwind. React Router
      is the maintained successor to the original Remix implementation plan.
- [x] **1.2** Added strict election, contest, candidate, measure, issue-lens,
      source, citation, brief-response, evidence-status, and correction-report
      contracts with tests.
- [x] **1.3** Added Ruff linting, documented local commands, and CI for API and
      web checks.
- [x] **1.4** Added the non-persistent browser-session foundation for selected
      contests and issue lenses.
- [x] **2.1, Measure D only** Created a metadata-only source-review queue;
      every source remains pending review.
- [x] **2.2, prerequisite** Created the private, versioned Cloud Storage bucket
      `gs://ballotsense-mvp-source-snapshots` for public source snapshots.
- [x] **2.2, snapshotting** Saved and SHA-256 hashed four supplied official
      Measure D PDFs in the private, versioned artifact store; created pending
      source records bound to each exact snapshot.
- [x] **2.2, review** Project owner approved all four Measure D source records
      on 2026-07-12.
- [x] **2.3** Created six locator-bound, verbatim extraction candidates from
      the approved source snapshots and retained their OCR-review notes.
- [x] **2.4** Project owner approved all six excerpts; promoted them to the
      retrieval-eligible corpus with reviewer and review-time audit fields.
- [x] **2.5** Project owner approved the Measure D coverage matrix, deliberate
      public-education evidence gap, retrieval-policy fixtures, and correction
      checklist on 2026-07-12. No embeddings or Gemini voter-answer calls have
      been made.
- [x] **3.1, database** Created the development Firestore Native-mode standard
      database in `us-west1` and enabled Firestore, Cloud Run, Artifact
      Registry, and Secret Manager APIs. Firestore security rules were not
      changed.
- [x] **3.2–3.3, local foundation** Added an approved-only Firestore source
      repository and idempotent non-public ingestion command. Local Python
      Application Default Credentials are configured for development access.
- [x] **3.3, first corpus ingestion** Wrote four approved Measure D source
      records and six approved chunks to development Firestore in ingestion run
      `ingest-9b1f4a18-d9c8-470f-8817-6461d262a994`. Provenance was verified;
      embeddings remain intentionally absent.
- [x] **3.3, embedding contract** Project owner approved Vertex AI
      `gemini-embedding-001` with 768 output dimensions on 2026-07-12. Corpus
      chunks use `RETRIEVAL_DOCUMENT`; voter queries must use
      `RETRIEVAL_QUERY`. Firestore vector retrieval must use cosine distance.
- [x] **3.3, first embedding run** Vertex AI created 768-dimensional document
      vectors for the six approved Measure D chunks in run
      `embed-402d6c32-f875-4aed-84e0-d086b5152b81`. The Firestore vector index
      is provisioning; no retrieval query has been issued.

## Phase 0 — Product decisions and governance

**Target duration:** Week 0 through Week 1  
**Goal:** Lock a deliberately small, safe first slice before building features.

### 0.1 Create the MVP decision packet

**Owner:** AI prepares; you approve.

1. Create `docs/mvp-decision-packet.md` with the decisions below and a dated
   approval section.
2. State the unchanging product rule: BallotSense is a cited research assistant,
   not a voting recommender.
3. State the initial geography and election: archived June 2026 primary,
   Santa Clara County scope.
4. State that the first public-facing dataset is limited to one measure and one
   candidate race, not a whole ballot.
5. State that match scores, free-text political profiles, account creation, and
   ballot OCR are excluded from the first vertical slice.

**Output:** A short decision document that someone else can use to tell what is
in and out of the demo.

### 0.2 Select the first two demo contests

**Owner:** AI researches options; you choose and approve.

The AI must produce a short inventory of candidate options before asking for
approval. For each candidate contest or measure, the inventory contains:

- Official title and contest identifier.
- Jurisdiction and election date.
- Link to official ballot language or official voter guide.
- Availability of a source with stable page/heading locators.
- For a candidate race, availability of at least one filed statement or dated
  official campaign statement for each candidate.
- Known source gaps and whether the contest is suitable for a transparent
  `no verified position found` example.

**Default recommendation:** start with one ballot measure first because
official legal text makes it easier to prove the citation workflow. Add one
race with two or more candidates second, because it tests attribution and fair
evidence-coverage presentation.

**You approve:** the exact measure and exact candidate race. Do not begin
ingestion until this decision is recorded.

### 0.3 Confirm issue lenses

**Owner:** Shared.

1. Begin with four lenses: housing affordability, public safety,
   climate/environment, and public education.
2. Write a plain-language description and bounded retrieval vocabulary for each
   lens.
3. State what each lens cannot imply. For example, a housing statement does not
   automatically establish a position on taxation, environmental regulation, or
   homelessness.
4. Do not collect free-form values or party affiliation.

**You approve:** the initial four lens names and descriptions.

### 0.4 Confirm source and review ownership

**Owner:** You decide; AI records and operationalizes.

1. Name the human source reviewer and a backup reviewer.
2. Decide whether a second reviewer is required for a contested claim or
   campaign source.
3. Decide the correction-response target, for example: acknowledge a report in
   two business days and correct/annotate it after review.
4. Approve the first-release source hierarchy:
   - Tier 1: official ballot language, voter guides, and elections-office
     material.
   - Tier 2: filed candidate statements.
   - Tier 3: dated official campaign statements, clearly labelled.
5. Confirm that third-party scorecards, endorsements, news reporting, and social
   posts remain out of scope.

### Phase 0 acceptance checklist

- [x] Exact demo measure approved.
- [x] Exact demo candidate race approved.
- [x] Four issue lenses approved.
- [x] Source reviewer and correction owner named.
- [x] Product boundary approved.
- [x] Source policy reviewed after the addition of the ballot-argument source
      type.
- [x] The first source inventory has an acquisition plan for every chosen
      contest.

**Stop point:** Do not move to Phase 1 or 2 until all items above are checked.

## Phase 1 — Engineering foundation

**Target duration:** Week 1 through Week 2  
**Goal:** Make the small application safely runnable and testable without real
election data.

### 1.1 Lock the repository structure

**Owner:** AI.

1. Keep `ballotsense_api/` as the FastAPI package.
2. Create a separate React Router framework application directory, for example
   `web/`, using React and Tailwind only for component styling. This is the
   maintained successor to Remix for new applications.
3. Add a top-level architecture diagram and a concise developer setup section
   to the README if the existing documents do not already cover them.
4. Do not move secret values into the repository. Create only an
   `.env.example` with variable names and no values if configuration is needed.
5. Add a `Makefile` or documented commands for test, format, lint, and local
   run tasks.

**Verify:** A new developer can find the API, web app, documentation, and local
commands without guessing.

### 1.2 Complete API contracts

**Owner:** AI.

1. Keep source, chunk, citation, and cited-claim Pydantic models strict.
2. Add contracts for election, contest, candidate, measure, issue lens, brief
request, brief response, evidence status, and correction report.
3. Represent evidence state explicitly: `supported`, `insufficient_evidence`,
   `pending_review`, and `not_covered`.
4. Require at least one citation for every factual claim.
5. Require attribution for filed candidate and campaign statements.
6. Make a recommendation or numeric candidate score invalid at the response
   schema level where practical.

**Verify:** Unit tests prove invalid sources, missing citations, wrong source
types, and prohibited response types cannot pass validation.

### 1.3 Set up quality controls

**Owner:** AI.

1. Add formatting and lint configuration for Python and TypeScript.
2. Add unit-test commands for API and web app.
3. Add a CI workflow that runs formatting, linting, and tests on pull requests.
4. Add dependency and secret scanning appropriate to the hosting provider.
5. Keep test fixtures synthetic until Phase 2 approval.

**Verify:** Clean checkout → dependency install → test command is documented
and succeeds locally.

### 1.4 Build the non-persistent session foundation

**Owner:** AI.

1. In the web app, hold selected lenses and chosen demo contests in browser
   memory only.
2. Do not add authentication, user database, analytics identifiers, or server
   persistence for voter choices.
3. Add a local-data reset function before adding notes/bookmarks.
4. Document exactly what browser state is retained and for how long.

**Verify:** Reload/clear behavior is understandable and no preference data is
sent to logs or stored by the API.

### Phase 1 acceptance checklist

- [x] API and web app start locally.
- [x] Synthetic contract tests pass.
- [x] A missing citation causes a test failure.
- [x] No secret, ballot image, or personal voter data is in Git.
- [x] Quality commands are documented and automated.

## Phase 2 — Curated source corpus and review workflow

**Target duration:** Week 2 through Week 4  
**Goal:** Build the reviewed evidence set before adding live AI answers.

### 2.1 Gather source candidates

**Owner:** AI gathers; reviewer approves.

For each selected contest, the AI creates a source inventory row with:

1. Title, publisher, canonical URL, source tier, election, jurisdiction, and
   contest/entity mapping.
2. Publication date if known and retrieval timestamp.
3. Whether it is a PDF, web page, candidate filing, or campaign source.
4. Whether the source has stable page/heading locators.
5. Retrieval status: `candidate`, `fetched`, `pending_review`, `approved`, or
   `rejected`.
6. Reason for inclusion and potential bias/attribution note.

**Rule:** Do not put a document into vector retrieval merely because it is
publicly available.

### 2.2 Snapshot and hash approved-to-review documents

**Owner:** AI after you authorize storage/location; reviewer observes.

1. Fetch each permitted source from its canonical URL.
2. Store an immutable source snapshot in the approved artifact location.
3. Compute the SHA-256 hash of the exact stored artifact.
4. Record retrieval time, source URL, source type, source version/date, and
   hash in the source record.
5. Do not download or store ballot photos from users. These are not corpus
   artifacts.
6. If a source later changes, ingest a new version; do not rewrite the old
   review record.

**Verify:** Every saved document can be tied back to a URL and a hash.

### 2.3 Extract and chunk source text

**Owner:** AI; reviewer checks output.

1. Extract text from digital sources; use document OCR only if source text is
   unavailable or unusable.
2. Preserve page number, heading, and source offsets where possible.
3. Split into coherent chunks that keep speaker attribution and qualifiers with
   the claim they modify.
4. Map every chunk to the election and contest; map candidate statements to a
   candidate ID and measure text to a measure ID.
5. Do not create chunks from AI summaries. A chunk is a verbatim source excerpt.
6. Mark uncertain extraction output for reviewer attention.

**Verify:** A reviewer can open any chunk and locate its exact original text.

### 2.4 Review and approve chunks

**Owner:** Human reviewer; AI provides tooling/checklist.

The reviewer checks, for every source/chunk:

1. Correct source identity and URL.
2. Correct election, contest, candidate, or measure mapping.
3. Correct source-tier and attribution label.
4. Text is faithful and locator is usable.
5. No misleading omission or altered context.
6. Approval, rejection, or pending status with reviewer and time recorded.

**Verify:** Only approved chunks are visible to the retrieval repository.

### 2.5 Create corpus fixtures and coverage matrix

**Owner:** AI prepares; reviewer approves.

1. Create a contest coverage matrix: source types available per candidate,
   measure, and issue lens.
2. Include at least one deliberate evidence gap to exercise abstention.
3. Prepare test fixtures for correct source, wrong contest, rejected source, and
   no-source scenarios.
4. Create the first reviewer-facing correction checklist.

### Phase 2 acceptance checklist

- [x] Every approved source has URL, publisher, hash, date/retrieval time,
      source tier, reviewer, and review state.
- [x] Every approved chunk has a contest binding and locator.
- [x] No generated summaries are stored as source chunks.
- [x] At least one source gap is deliberately represented.
- [x] Reviewer can reproduce a source claim from raw material.

**Stop point:** Do not generate embeddings or call Gemini for voter answers
until the approved corpus passes this checklist.

## Phase 3 — Firestore and retrieval

**Target duration:** Week 4 through Week 5  
**Goal:** Make only relevant, approved chunks retrievable.

### 3.1 Obtain cloud prerequisites

**Owner:** You grant access; AI configures after authorization.

You provide or approve:

1. GCP project and billing account.
2. Permission to create or use Firestore Native mode, Cloud Run, Cloud Storage,
   Secret Manager, Artifact Registry, and Cloud Logging.
3. A least-privilege service-account strategy.
4. A development environment first; do not provide production keys to a local
   repository.
5. Gemini API access through Secret Manager or approved workload identity.

**Stop point:** The AI does not create cloud resources, read billing details, or
use secret values without explicit authorization.

### 3.2 Define Firestore schema and indexes

**Owner:** AI.

1. Implement `elections`, `jurisdictions`, `contests`, `candidates`,
   `measures`, `sources`, `source_chunks`, `ingestion_runs`, `claim_audits`,
   and `correction_reports` as specified in the system design.
2. Include election ID, contest ID, source ID, review status, source type, and
   entity IDs as filterable fields.
3. Add native vector indexes to `source_chunks.embedding` using **cosine
   similarity** only.
4. Version the embedding model and corpus release.
5. Apply least-privilege IAM; do not change Firestore security rules without
   your approval.

### 3.3 Implement ingestion repository

**Owner:** AI.

1. Implement a Firestore repository behind the existing source-repository
   interface.
2. Write an idempotent ingestion command/job: rerunning a source does not
   duplicate it.
3. Refuse to embed or expose `pending` and `rejected` chunks.
4. Create a Cloud Run Job for batch ingestion; do not turn ingestion into a
   public API endpoint.
5. Record source hash, ingestion version, and errors.

### 3.4 Implement filtered retrieval

**Owner:** AI.

1. Build one query per contest/entity plus selected issue lens.
2. Apply hard filters before or with vector search: supported election,
   confirmed contest, matching candidate/measure where applicable, and approved
   review status.
3. Retrieve a bounded, diverse evidence packet; do not return dozens of near
   duplicates.
4. Preserve source IDs, chunk IDs, locators, source type, and dates in every
   result.
5. Return `insufficient_evidence` before generation when no qualifying chunk
   exists.

### 3.5 Test retrieval boundaries

**Owner:** AI.

1. Test expected chunk retrieval for every demo question.
2. Test that wrong-election chunks cannot return.
3. Test that wrong-contest and wrong-candidate chunks cannot return.
4. Test that pending/rejected sources cannot return.
5. Test source-type diversity and stable source IDs.

### Phase 3 acceptance checklist

- [ ] Firestore uses native cosine vector search.
- [ ] Only approved chunks are retrievable.
- [ ] Every retrieval result includes provenance and locator.
- [ ] Boundary tests for wrong election/contest/source pass.
- [ ] Ingestion can rerun without corrupting the corpus.

## Phase 4 — Cited generation and validation

**Target duration:** Week 5 through Week 6  
**Goal:** Produce safe, short, cited briefs from retrieved evidence only.

### 4.1 Define final brief response schema

**Owner:** AI.

1. Add response objects for contest context, plain-language explanation,
   factual claims, candidate/campaign statements, evidence coverage, citation
   cards, and insufficient-evidence states.
2. Forbid `recommendation`, `match_score`, `rank`, and free-form political
   inference fields.
3. Require citation objects with source ID, chunk ID, locator, and public source
   URL for every displayable factual claim.
4. Require a source-type label and attribution where required.
5. Define a response size limit so the app returns a readable brief rather than
   an essay.

### 4.2 Build the bounded Gemini call

**Owner:** AI after Gemini access is authorized.

1. Build the evidence packet from the Phase 3 retrieval results only.
2. Include source IDs, chunk IDs, source types, dates, locators, and verbatim
   text in the model input.
3. Instruct Gemini to use only the packet, return strict JSON, preserve
   attribution, avoid endorsements, and abstain when evidence is missing.
4. Set conservative output length and deterministic settings as supported by the
   selected Gemini model.
5. Do not send voter address, ballot image, personal note, or durable profile
   to the model.

### 4.3 Implement deterministic output validation

**Owner:** AI.

1. Validate schema before parsing for display.
2. Validate that every citation references a chunk in the supplied evidence
   packet.
3. Validate source review status, contest/entity binding, and permitted source
   type again at response time.
4. Check required attribution for candidate/campaign statements.
5. Reject prohibited recommendation/ranking language using explicit policy
   checks.
6. If output is invalid, retry once with corrective feedback or return a safe
   insufficient-evidence response.
7. Record a redacted claim audit containing corpus version, chunk IDs, validator
   outcome, and no voter-specific content.

### 4.4 Build the evaluation suite

**Owner:** AI creates; reviewer scores.

1. Create a fixed set of questions for the measure, candidate race, evidence
   gaps, ambiguous language, and misleading source material.
2. Add a human scoring rubric: citation resolves, citation supports claim,
   attribution is correct, claim is non-recommendatory, and abstention is
   correct when needed.
3. Add automated negative tests with fabricated citations, wrong-contest
   citations, uncited factual statements, and party-based inference.
4. Run the suite against a fixed corpus version before every demo deployment.

### Phase 4 acceptance checklist

- [ ] Every factual claim in the demo response has valid evidence.
- [ ] Invalid output is blocked from the UI.
- [ ] No-answer cases return an honest evidence-gap state.
- [ ] Human review finds no unsupported claim in the acceptance set.
- [ ] Generated responses do not rank or recommend choices.

**Stop point:** Do not connect model output to a voter UI until the acceptance
suite passes.

## Phase 5 — Mobile research UI

**Target duration:** Week 6 through Week 8  
**Goal:** Make the proof-carrying guide useful on a phone.

### 5.1 Build the first screens in this exact order

**Owner:** AI.

1. Welcome/trust screen: explain citation-first research, non-endorsement, and
   privacy promise.
2. Issue-lens screen: select up to three approved lenses; show their plain
   definitions.
3. Supported-contest screen: choose the measure or race from the archive demo;
   no address or ballot scan yet.
4. Contest brief screen: what the measure changes or what the office controls,
   then the cited research brief.
5. Evidence coverage screen: show what source type is available for each
   candidate/lens; show gaps clearly.
6. Citation drawer/detail screen: publisher, date, source type, locator,
   excerpt, and link to original material.
7. Local note/bookmark feature and a clear-local-data action.

### 5.2 Apply UX constraints

**Owner:** AI; you approve wording.

1. Do not show scores, implied candidate order, colored good/bad labels, or a
   "recommended" action.
2. Do not hide missing evidence below a "read more" control.
3. Use explicit labels such as `Official election material`, `Filed candidate
   statement`, and `Campaign statement`.
4. Ensure all clickable proof controls work with keyboard and screen reader.
5. Use Tailwind utilities; do not create separate CSS files unless a complex
   override is required.
6. Keep every primary task usable in a single narrow mobile column.

### 5.3 Test the UI

**Owner:** AI automates; you/reviewers perform manual checks.

1. Test phone and desktop breakpoints.
2. Test keyboard-only navigation and screen-reader labels.
3. Test citation opening from every claim.
4. Test missing-evidence and source-pending states.
5. Test that local notes never travel in API requests.
6. Test that no user input changes source citations or claim IDs.

### Phase 5 acceptance checklist

- [ ] A voter can reach a cited brief in three clear steps.
- [ ] Every displayed claim exposes its proof.
- [ ] Source types and uncertainty are unmistakable.
- [ ] The guide is usable on a mobile device without an account.
- [ ] Accessibility checks pass for the MVP flows.

## Phase 6 — Archive demo, review, and correction loop

**Target duration:** Week 8 through Week 10  
**Goal:** Test comprehension and trust with people before broader coverage.

### 6.1 Prepare staging deployment

**Owner:** AI deploys after your cloud approval.

1. Provision separate development and staging configuration.
2. Deploy frontend and API as separate Cloud Run services.
3. Use Firestore Native mode and approved corpus version only.
4. Put source artifacts in a private Cloud Storage bucket; do not include ballot
   images.
5. Configure Secret Manager, least-privilege service accounts, logging,
   monitoring, error reporting, budgets, and a rollback path.
6. Ensure personalized responses are not cached by CDN or shared server cache.

### 6.2 Run the demo review

**Owner:** Shared.

1. Recruit a small, varied group of test voters.
2. Ask them to identify whether a statement is official, candidate-authored, or
   campaign-authored.
3. Ask them to locate source proof for a displayed claim.
4. Ask them what `No verified position found` means; it must not be interpreted
   as opposition.
5. Observe whether users perceive a hidden recommendation.
6. Record only consented research feedback; do not record personal ballot
   choices.

### 6.3 Resolve issues and demonstrate correction handling

**Owner:** AI fixes; reviewer approves.

1. Triage source errors, unclear wording, invalid citations, and privacy issues
   by severity.
2. Correct corpus records with new versions; never silently overwrite a source
   history.
3. Repeat evaluation and UI tests after every source/citation correction.
4. Test a correction report from submission through reviewer resolution.

### Phase 6 acceptance checklist

- [ ] Test voters understand this is research support, not an endorsement.
- [ ] Test voters can distinguish source types.
- [ ] No high-severity citation, privacy, or accessibility defect remains.
- [ ] Correction workflow works end to end.
- [ ] Staging rollback has been exercised once.

## Phase 7 — Optional ballot discovery and OCR

**Target duration:** Week 10 through Week 12  
**Goal:** Add convenience only after the core cited guide is trusted.

### 7.1 Address-based discovery comes first

**Owner:** AI after you authorize an approved geographic source/provider.

1. Select an address-to-district provider or official jurisdiction source.
2. Resolve an address only for the live request; do not persist raw address.
3. Return inferred contests and require user confirmation.
4. Record no address in API logs or claim audits.
5. Keep manual contest picker available as fallback.

### 7.2 Decide whether OCR is worth adding

**Owner:** You approve; AI supplies feasibility and privacy assessment.

OCR may proceed only if it clearly improves ballot discovery over address entry
and the team can prove in-memory-only image handling. If it is not clearly
worth it, skip OCR for the archive demo.

### 7.3 Implement OCR only after approval

**Owner:** AI.

1. Accept an image only after explicit warning to use an unmarked ballot or
   official sample ballot.
2. Enforce image type, size, and request-time limits.
3. Process bytes only in memory; do not store image data in Firestore, Cloud
   Storage, logs, analytics, or model-memory features.
4. Use Gemini multimodal extraction only to identify contest labels and
   candidate/measure names.
5. Release image memory after the request succeeds or fails.
6. Show an editable confirmation list; no contest is researched until confirmed.
7. Add automated no-storage tests and manual red-team tests with a marked
   ballot image.
8. Retain a feature flag that disables OCR without disabling the research guide.

### Phase 7 acceptance checklist

- [ ] Address or OCR errors cannot silently alter the contest list.
- [ ] No ballot image persistence is detected in tests, storage, or logs.
- [ ] Manual contest selection remains available.
- [ ] OCR can be disabled independently.

## Phase 8 — November/public release decision

**Target duration:** Week 12 onward  
**Goal:** Make a documented go/no-go decision based on quality, not enthusiasm.

### 8.1 Build the release candidate corpus

**Owner:** AI gathers and stages; reviewer approves.

1. Wait until official November ballot and voter-guide materials are available.
2. Build a contest coverage matrix for the exact public geography.
3. Repeat Phase 2 source ingestion and review for every contest intended for
   display.
4. Publish the coverage scope in the UI; do not imply whole-ballot coverage if
   it is partial.

### 8.2 Run the public-release checks

**Owner:** AI validates; you and reviewers approve.

1. Rerun citation-support, abstention, attribution, retrieval-boundary, and
   accessibility evaluations against the release corpus.
2. Perform load, cost, security, and rollback testing.
3. Confirm Cloud Run scale limits, budgets, on-call contact, incident response,
   correction owner, and corpus freeze/version.
4. Recheck that user address, ballot image, and choice data are absent from
   persistent systems and logs.
5. Obtain written sign-off from the product owner and source reviewer.

### 8.3 Go/no-go rule

Launch only if all conditions are true:

- [ ] Each displayed contest meets the published source-coverage standard.
- [ ] Every acceptance-set claim is supported by its reviewed citation.
- [ ] Missing evidence displays as a gap, never as a negative inference.
- [ ] No storage path exists for ballot images or voter selections.
- [ ] Monitoring, correction, incident response, and rollback have named
      owners.
- [ ] Product owner and source reviewer signed off.

If any item is false, preserve the archive demo, document the gap, and target a
later election. Do not rush the public launch.

## AI task handoff format

When you tell the AI to execute the next task, use this format:

> Execute Phase `<number>`, Task `<number>`. Read the three governing docs,
> inspect the current repository, implement only that task, run relevant tests,
> update me with evidence, and stop at any approval gate.

Example:

> Execute Phase 1, Task 1.2. Read the governing docs, add only the missing API
> response contracts and tests, and do not begin Firestore or Gemini work.

## What you need to do now

Complete Phase 0 in this order:

1. Tell the AI to research and present options for the first archived ballot
   measure and candidate race.
2. Choose the two exact demo contests from that inventory.
3. Approve the four initial issue lenses or revise them.
4. Name the source reviewer and correction owner.
5. Tell the AI to record the decisions in `docs/mvp-decision-packet.md`.
6. Then tell the AI to begin Phase 1, Task 1.1.

The next recommended instruction is:

> Execute Phase 0, Task 0.2: research official June 2026 Santa Clara County
> primary sources and present a small choice of one ballot measure and one
> candidate race suitable for the first cited archive demo. Do not ingest or
> build new product features yet.
