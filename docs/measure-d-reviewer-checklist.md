# Measure D reviewer correction checklist

Use this checklist for every correction, source replacement, or chunk dispute.
It is for the archived June 2026 demo and does not authorize a change to an
approved source without recording a new review decision.

## Intake

- [ ] Record the report date, reporter contact if voluntarily provided, and a
      concise issue description. Do not request or retain ballot images, voter
      addresses, vote selections, or political preferences.
- [ ] Record the source ID, chunk ID, contest ID, and displayed locator when
      applicable.
- [ ] Classify the issue: source identity, canonical URL, hash/snapshot,
      contest binding, transcription/locator, attribution, missing evidence,
      or display issue.

## Verify

- [ ] Open the private snapshot using the recorded `gs://` URI and compare its
      SHA-256 hash with the source record.
- [ ] Confirm the canonical URL, publisher, election, jurisdiction, contest,
      source tier, and review history.
- [ ] Compare the whole approved excerpt with its original page or heading;
      check that a qualifier, speaker, and surrounding context were not lost.
- [ ] For a ballot argument or rebuttal, confirm that the proposed display is
      attributed to its speaker side and is not phrased as a neutral fact.
- [ ] For an evidence gap, confirm that the correct resolution is an
      `insufficient_evidence` or `not_covered` result rather than a new claim.

## Resolve and audit

- [ ] Choose: no change, annotate, reject source/chunk, replace with a new
      source version, or create a corrected chunk.
- [ ] If source content changed, snapshot the new version under a new GCS
      object path, compute a new hash, and create a new review record; never
      overwrite the prior reviewed record.
- [ ] Record reviewer, decision time, rationale, affected source/chunk IDs,
      and whether an existing citation or corpus release must be withdrawn.
- [ ] Re-run corpus validation before publishing any correction.

## Initial owner and service target

- **Correction owner:** Project owner (user)
- **Acknowledgement/correction target:** not yet set by the product owner.
