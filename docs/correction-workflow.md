# BallotSense correction workflow

Last updated: 2026-07-12

## Purpose

The correction workflow lets a user report a possible problem with a displayed
citation or claim. It is part of the citation-first trust model, not a general
feedback or voter-profile form.

## User-facing flow

1. User opens a cited claim's source proof.
2. User chooses `Report an issue with this source`.
3. User selects an issue type:
   - misleading summary
   - incorrect source
   - broken source link
   - privacy concern
   - other
4. User writes a short description of what the reviewer should check.
5. BallotSense submits the report with the citation binding.

The UI explicitly tells users not to include vote choice, address, email, phone
number, or private local note.

## Stored fields

Correction reports are stored with:

- report ID
- creation timestamp
- review status
- election ID
- contest ID
- lens ID
- source ID
- chunk ID
- issue type
- redacted issue description
- whether redaction was applied

Correction reports do not store:

- voter name
- email address
- phone number
- street address
- ballot choice
- party affiliation
- private session note
- account ID
- durable voter profile

## Redaction

The backend redacts obvious personal data before storage:

- email-like strings
- phone-like strings
- street-address-like strings
- first-person vote-preference phrases such as `I will vote yes`

The original free-text description is not stored. Only the redacted description
is written to the correction report record.

## API

Endpoint: `POST /v1/corrections`

Required request fields:

- `election_id`
- `contest_id`
- `lens_id`
- `source_id`
- `chunk_id`
- `issue_type`
- `description`

The request schema rejects extra fields. This prevents accidental submission of
local notes, vote choice fields, or other unsupported voter-profile data.

## Reviewer handling

The reviewer should:

1. Open the referenced source and chunk.
2. Compare the reported claim, source locator, and source type.
3. Mark the report as valid, invalid, duplicate, or needing more review in the
   reviewer workflow.
4. If valid, create a corrected corpus/version record. Do not silently rewrite
   prior source history.
5. Rerun relevant retrieval, generation, and UI checks after any correction.

The first implementation stores incoming reports as `pending`; reviewer status
transitions can be added after the first staged correction-report test.

## Staging verification

On 2026-07-12, the private staging workflow accepted a citation-bound report
through the frontend proxy route and stored it in Firestore as
`c734c6ef-c425-45df-b467-9eb5ecbef493`.

The stored record was verified to include only the citation binding and
redacted description. The submitted email and vote-preference phrase were
redacted before storage. A second request containing extra `vote_choice` and
`local_note` fields returned `422`.
