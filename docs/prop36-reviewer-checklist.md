# Proposition 36 reviewer checklist

## Scope

Corpus target: **Archived California November 2024 Proposition 36 demo corpus**

Master source: California Secretary of State, *Official Voter Information Guide,
November 5, 2024 General Election*

Manifest:
`data/source_snapshots/ca-general-2024-11-05/ca-prop-36-2024/master-pdf-manifest.json`

Review packet:
`data/review_packets/prop-36-2024.json`

Master PDF SHA-256:
`4f7fef63bddb5c60aaabda673b57ae4375105ce941d2ff9dc9d7136aee7e4ef4`

## Review rule

Do not approve the packet unless every retained chunk is:

1. copied from the official master PDF,
2. mapped to Proposition 36,
3. paired with a usable page locator,
4. labeled as neutral analysis or attributed argument/rebuttal where relevant,
5. free of generated summaries, and
6. safe to promote into the approved retrieval corpus.

## Candidate chunks to review

| Chunk ID | Locator | Treatment before approval |
| --- | --- | --- |
| `ca-prop-36-2024-title-summary` | Official VIG PDF p. 58, title and summary | Neutral Attorney General title/summary. Check bullets and fiscal summary. |
| `ca-prop-36-2024-lao-background` | Official VIG PDF pp. 58-59, LAO background | Neutral Legislative Analyst background. Check cross-page join. |
| `ca-prop-36-2024-lao-proposal` | Official VIG PDF pp. 59-60, LAO proposal description | Neutral Legislative Analyst proposal. Check theft/drug/treatment/warning sections. |
| `ca-prop-36-2024-lao-fiscal-effects` | Official VIG PDF pp. 60-61, LAO fiscal effects | Neutral Legislative Analyst fiscal effects. Check cost and Proposition 47 savings language. |
| `ca-prop-36-2024-argument-in-favor` | Official VIG PDF p. 62, argument in favor | Attributed ballot argument; not neutral fact. Preserve author/source label. |
| `ca-prop-36-2024-rebuttal-to-favor` | Official VIG PDF p. 62, rebuttal to argument in favor | Attributed rebuttal by opponents; not neutral fact. |
| `ca-prop-36-2024-argument-against` | Official VIG PDF p. 63, argument against | Attributed ballot argument; not neutral fact. Preserve author/source label. |
| `ca-prop-36-2024-rebuttal-to-against` | Official VIG PDF p. 63, rebuttal to argument against | Attributed rebuttal by proponents; not neutral fact. |
| `ca-prop-36-2024-text-p126` | Official VIG PDF p. 126, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p127` | Official VIG PDF p. 127, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p128` | Official VIG PDF p. 128, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p129` | Official VIG PDF p. 129, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p130` | Official VIG PDF p. 130, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p131` | Official VIG PDF p. 131, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p132` | Official VIG PDF p. 132, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p133` | Official VIG PDF p. 133, text of proposed laws | Official measure text. Keep page-level or split by statute section. |
| `ca-prop-36-2024-text-p134` | Official VIG PDF p. 134, text of proposed laws | Official measure text tail. Confirm it is useful enough to keep. |

## Approval procedure

If the reviewer approves the packet:

1. Set `review_decision` to `approved`.
2. Set `reviewed_at` to the approval timestamp.
3. Keep `reviewer` as `Project owner (user)` unless a different reviewer signs off.
4. Promote with:

```bash
make promote-prop36-review
```

If any chunk needs work, keep `review_decision: pending` and edit, split, or
reject the chunk before promotion.
