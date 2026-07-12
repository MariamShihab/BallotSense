# Phase 8 source readiness check — 2026-07-12

Targets:

- Proposition 1 — primary target
- Proposition 45 — secondary target

This is a source-readiness check only. It does not approve, snapshot, ingest,
embed, or display any November 2026 source.

## Official sources checked

| Source | Publisher | Result |
| --- | --- | --- |
| General Election — November 3, 2026 | California Secretary of State | Available; confirms election information and key dates. |
| Qualified Statewide Ballot Measures | California Secretary of State | Available; lists Proposition 1 and Proposition 45. |
| Official Voter Information Guide | California Secretary of State | Page exists, but says the November 3, 2026 guide will be available in September 2026. |
| SB 417 PDF | California Secretary of State | Available as Proposition 1 underlying measure text. |
| 25-0023A1 PDF | California Department of Justice / Attorney General | Available as Proposition 45 initiative text. |

## Readiness summary

| Target | Current status | Ready for snapshot? | Ready for ingestion? | Decision |
| --- | --- | --- | --- | --- |
| Proposition 1 | Qualified measure listing and measure-text PDF available; voter-guide package is not yet published. | No | No | Monitor |
| Proposition 45 | Qualified measure listing and initiative-text PDF available; voter-guide package is not yet published. | No | No | Monitor |

## Missing before release-candidate corpus work

For each target measure, wait for:

- published official voter guide page or PDF,
- official title and summary suitable for voter-facing citation,
- official fiscal or legislative analysis,
- official argument in favor,
- official argument against,
- official rebuttals, if any,
- stable page/heading locators.

Until these materials exist, BallotSense should not snapshot or ingest the
November release-candidate corpus.

## Machine-readable readiness matrix

The corresponding readiness matrix is:

`data/coverage/november-2026-source-readiness.json`

## Repeatable monitor

Run:

```bash
make check-november-sources
```

The monitor checks official SOS pages only. It does not snapshot, hash, ingest,
embed, or store documents.

## Current decision

Continue monitoring. Do not ingest Proposition 1 or Proposition 45 yet.

The next Phase 8 action is to rerun the monitor when voter-guide materials are
published or updated, expected in or around September 2026 based on the official
SOS voter-guide page.
