# Phase 8 transition — public release decision

Date: 2026-07-12

Phase 7 archive-demo scope is complete:

- Address discovery remains manual-only for the archive demo.
- Official Santa Clara County ROV outbound links are provided as fallback.
- OCR and ballot image uploads are skipped for the archive demo.
- Deferred scope is tracked in [deferred features](deferred-features.md).

## Next objective

Phase 8 is a go/no-go planning phase for any November 3, 2026 public-release
candidate. The goal is not to launch by enthusiasm; it is to decide whether the
corpus, privacy posture, evaluation results, monitoring, correction workflow,
and operations are strong enough for a public demo.

## First Phase 8 tasks

1. Confirm the exact November 3, 2026 geography and public-demo scope.
2. Wait for or locate official November ballot/voter-guide materials.
3. Build a release-candidate source inventory before ingesting anything.
4. Publish the intended coverage scope in the UI; do not imply whole-ballot
   coverage if the corpus is partial.
5. Re-run citation-support, abstention, attribution, retrieval-boundary, and
   accessibility checks against the release-candidate corpus.

## Recommended starting point

Start Phase 8 with a November corpus planning document:

- election date and geography,
- intended contests/measures,
- official source locations,
- source gaps,
- reviewer responsibilities,
- go/no-go checklist.
