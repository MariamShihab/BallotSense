# MVP decision packet — draft

**Status:** Phase 0 approved; Phase 2 source review in progress  
**Phase:** 0 — Product contract and governance  
**Dataset:** Archived June 2, 2026 California Statewide Direct Primary Election  
**Geography:** Santa Clara County

This document records the decisions required before real election material may
enter the BallotSense corpus. It is a planning/source-inventory artifact only;
no source listed here has been approved, ingested, embedded, or made available
to an AI model.

## 1. Product contract to approve

- [ ] BallotSense provides cited research assistance, not voting
      recommendations.
- [ ] The MVP has no numeric candidate match score or candidate ranking.
- [ ] The MVP has no free-text values input, party-based inference, account, or
      durable voter profile.
- [x] The initial issue lenses are: housing affordability, public safety,
      climate/environment, and public education.
- [ ] By default, ballot images, addresses, selected lenses, notes, and voting
      choices are not stored on backend infrastructure.
- [x] The first demo shows one ballot measure before it shows a candidate race.
- [ ] The source policy in [source-policy.md](source-policy.md) is approved.

## 2. Recommended first ballot measure

### Recommendation: Measure D — Santa Clara Valley Open Space Authority

**Title:** Voter-Sponsored Initiative Special Parcel Tax  
**Ballot:** June 2, 2026 Statewide Direct Primary Election  
**Vote threshold:** Majority vote  
**Why it is the strongest first vertical slice:**

- It connects directly to the initial climate/environment lens while also
  exercising taxes, public-safety-related claims, land use, and oversight.
- The official County measure page provides ballot language, an impartial
  analysis, arguments for and against, and rebuttals—enough material to test
  source type and attribution without relying on web commentary.
- The measure presents genuine tradeoffs, so the first brief can demonstrate
  that BallotSense explains evidence rather than recommends a choice.

**Official source inventory — all pending human review:**

| Source | Type | Intended use | Status |
| --- | --- | --- | --- |
| [County list of local measures](https://vote.santaclaracounty.gov/list-local-measures-3) | Official County election page | Official ballot question, vote threshold, and document index | Candidate source |
| [Impartial analysis](https://files.santaclaracounty.gov/exjcpb1296/2026-03/measure-d-impartial-analysis-santa-clara-valley-open-space-authority-filed-3.17.26_redacted.pdf?VersionId=9ZdJxDtFoadJsAqbKoFcE0R6fr5LvHUI) | Official impartial analysis | Factual explanation of what the measure does | Candidate source |
| [Argument in favor](https://files.santaclaracounty.gov/exjcpb1296/2026-03/ballot-argument-form-for_dated_redacted.pdf?VersionId=aHQ5TJnAUE2UShteHxIMmSvbbevkkl8h) | Officially filed ballot argument | Attributed proponent argument only | Candidate source |
| [Rebuttal to argument in favor](https://files.santaclaracounty.gov/exjcpb1296/2026-03/measure-d-rebuttal-to-argument-in-favor-santa-clara-valley-osa_redacted.pdf?VersionId=WvSi9f3rR5DmTRCrta6hdPthxJ8cGae.) | Officially filed ballot rebuttal | Attributed rebuttal only | Candidate source |
| [Rebuttal to argument against](https://files.santaclaracounty.gov/exjcpb1296/2026-03/measure-d-rebuttal-to-argument-against-santa-clara-valley-osa_redacted.pdf?VersionId=oXgr4D5Ta6lKNgjWYNkJwrqIL2Mw2wo3) | Officially filed ballot rebuttal | Attributed rebuttal only | Candidate source |

**Review note:** The County page also links an official primary argument against
Measure D. Its direct download needs a retrieval check before it can enter the
corpus; a source link alone is not approval.

### Alternative measure choices

| Measure | Why it could work | Reason it is not the first recommendation |
| --- | --- | --- |
| Measure C — Franklin-McKinley School District general obligation bond | Has official ballot language, impartial analysis, arguments, and rebuttals; strong public-education example. | More technical bond/assessed-value explanation makes the first source pipeline slightly harder. |
| Measure B — Palo Alto Unified School District parcel-tax renewal | Has official measure, arguments on both sides, rebuttals, and impartial analysis. | Narrower geography and a source document needs text-extraction quality review. |
| Measure A — City of San José transient occupancy tax increase | Clear tax-and-services question; County provides an impartial analysis. | No argument against was submitted, so it is less useful for demonstrating evidence symmetry and disagreement. |

## 3. Candidate-race options for the second vertical slice

The first candidate race begins only after the Measure D research brief passes
the Phase 4 citation and abstention checks.

### Recommended race: Board of Supervisors, District 1

**Candidates on the June 2026 ballot:** Rebecca Munson and Sylvia Arenas.  
**Why it is recommended:** It has exactly two candidates, the official qualified
candidate list records a filed candidate statement for both, and the office is a
useful test of multiple local issue lenses rather than one narrowly scoped
topic.

**Official source inventory — all pending human review:**

| Source | Type | Intended use | Status |
| --- | --- | --- | --- |
| [Qualified List of Local Candidates](https://files.santaclaracounty.gov/exjcpb1296/2026-04/qualified-list-local-on-ballot-rad-3.13.2026-v3.pdf?VersionId=1WnwGMDaWwwAbro3XtDAGzbZZqeaJnNY) | Official County candidate list | Confirms contest, candidates, and that both filed a candidate statement | Candidate source |
| [June 2026 County election resources](https://vote.santaclaracounty.gov/june-2-2026-statewide-direct-primary-election-resources) | Official County election page | Links to local candidates, candidate-statement process, and voter information resources | Candidate source |
| County Voter Information Guide for the relevant ballot | Official County voter guide | Expected source for the actual filed candidate statements | Must locate and review before ingestion |

**Important limit:** A filed-statement flag proves a statement was filed; it is
not itself the statement. The actual voter-guide statement must be retrieved,
versioned, and human-approved before BallotSense can show a candidate-position
claim.

### Alternative race: Santa Clara County District Attorney

**Candidates on the June 2026 ballot:** Jeff Rosen and Daniel Chung.  
**Why it could work:** Two candidates, both marked as having filed candidate
statements in the official qualified candidate list, and countywide relevance.

**Why it is not the first recommendation:** The office is most directly
connected to public safety, so it provides a narrower test of the initial
multi-lens experience than the Board of Supervisors race.

## 4. Source review and correction ownership

- **Primary source reviewer:** Project owner (user), assigned 2026-07-11
- **Backup reviewer:** Project owner (user), assigned 2026-07-11
- **Correction owner:** Project owner (user), assigned 2026-07-11
- **Second review needed for campaign material or a disputed claim:**
  [ ] Yes / [ ] No
- **Correction acknowledgement target:** [ ] Choose a response target

## 5. Approval record

Complete these before corpus ingestion begins.

- [x] Approve Measure D as the first vertical slice, or select another measure
      listed above. Approved 2026-07-11.
- [x] Approve Board of Supervisors, District 1 as the second vertical slice, or
      select the District Attorney race instead. Approved 2026-07-11.
- [x] Approve or revise the four issue lenses. Approved 2026-07-11.
- [x] Name the primary reviewer, backup reviewer, and correction owner.
      Project owner (user), assigned 2026-07-11.
- [ ] Approve the Phase 0 product contract in section 1.

**Product-owner name:** ____________________  
**Approval date:** ____________________

## 6. Next task after approval

The AI may then execute Phase 1, Task 1.1 (repository structure) and Phase 2,
Task 2.1 (formal source inventory). It must not ingest, embed, or generate from
any election source until the reviewer has approved the source records.

## 7. Source snapshot artifact store

**Provisioned:** 2026-07-12  
**Bucket:** `gs://ballotsense-mvp-source-snapshots`  
**Location:** `US-WEST1`

- Public access prevention is enforced.
- Uniform bucket-level access is enabled.
- Object versioning is enabled for source-document revision traceability.
- The bucket contains public election-source snapshots only. It must never hold
  ballot images, voter addresses, voter selections, or voter notes.
- No locked retention policy is configured, so a reviewer can correct or remove
  an erroneous snapshot through the documented correction process.
