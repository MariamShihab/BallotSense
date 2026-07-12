# BallotSense staging deployment

Last updated: 2026-07-12

## Scope

This staging environment is for the private archived June 2026 Measure D demo.
It is not public, does not change Firestore security rules, and does not use
production secrets.

## GCP project

- Project: `ballotsense-mvp`
- Region: `us-west1`
- Artifact Registry repo: `ballotsense-staging`
- Source snapshots bucket: `gs://ballotsense-mvp-source-snapshots`
- Staging secret container: `ballotsense-staging-runtime-config`

The staging secret container has no secret payload because the current runtime
uses Cloud Run service identity for Vertex AI and Firestore access.

## Cloud Run services

- API service: `ballotsense-api-staging`
- API service account:
  `ballotsense-api-staging@ballotsense-mvp.iam.gserviceaccount.com`
- Web service: `ballotsense-web-staging`
- Web service account:
  `ballotsense-web-staging@ballotsense-mvp.iam.gserviceaccount.com`

Both services are private. The API grants `roles/run.invoker` only to the web
staging service account.

## Images

- API image:
  `us-west1-docker.pkg.dev/ballotsense-mvp/ballotsense-staging/api:20260712-phase6-corrections`
- Current web image:
  `us-west1-docker.pkg.dev/ballotsense-mvp/ballotsense-staging/web:20260712-phase6-corrections`

## Verified behavior

The private frontend was tested through an authenticated local Cloud Run proxy:

```sh
gcloud run services proxy ballotsense-web-staging \
  --project=ballotsense-mvp \
  --region=us-west1 \
  --port=8011
```

Then the deployed frontend proxy route was tested with:

```sh
curl -sS -X POST http://127.0.0.1:8011/api/v1/briefs \
  -H 'Content-Type: application/json' \
  -d '{"election_id":"ca-scc-2026-primary","contest_id":"scvosa-measure-d","lens_ids":["climate-environment"]}'
```

Expected result: a `supported` Measure D climate/environment finding with the
`scvosa-measure-d-analysis-accountability` citation.

Unauthenticated direct access was checked:

- Direct web service request returns `403`.
- Direct API brief request returns `403`.

## Rollback

Rollback was exercised once by moving web traffic to
`ballotsense-web-staging-00002-rhd`, then restoring traffic to the corrected
revision `ballotsense-web-staging-00003-drr`.

After the Phase 6 internal review, the frontend was updated to
`ballotsense-web-staging-00004-qnx` with clearer source labels and
contest-specific brief headings.

After the Phase 6 correction workflow, the API was updated to
`ballotsense-api-staging-00002-4kw` and the frontend was updated to
`ballotsense-web-staging-00005-9r2`.

Current restore command:

```sh
gcloud run services update-traffic ballotsense-web-staging \
  --project=ballotsense-mvp \
  --region=us-west1 \
  --to-revisions=ballotsense-web-staging-00005-9r2=100
```

## Correction workflow verification

The deployed frontend proxy route was tested with `POST /api/v1/corrections`.
The staged test report ID was `c734c6ef-c425-45df-b467-9eb5ecbef493`.

Firestore stored the report with:

- citation binding to `scvosa-measure-d-impartial-analysis` and
  `scvosa-measure-d-analysis-accountability`
- status `pending`
- redacted description only
- `redaction_applied: true`

The same endpoint returned `422` when extra `vote_choice` and `local_note`
fields were submitted.

## Budget and logging

- Budget alert: `BallotSense staging budget`
- Budget id: `97ee0841-9824-4656-babc-c17bf46c2d28`
- Budget amount: `$10`
- Thresholds: 50%, 90%, 100%

Cloud Logging, Cloud Monitoring, and Error Reporting APIs are enabled for the
project. Cloud Run request logs were used during staging verification.
