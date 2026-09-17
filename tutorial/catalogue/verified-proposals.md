# Verified staging proposals

This is an audit record, not a set of stable IDs to copy. Each row was
submitted against the same converged Meridian catalogue on Orbit staging and
opened in the review UI immediately afterwards on 2026-08-15. Later
submissions can supersede earlier pending proposals; reruns always produce new
proposal IDs.

!!! note "Historical snapshot"
    This replay predates the required-reference diagnostic and sensitive-review
    acknowledgement fixes. The proposal IDs and observations below are kept as
    an audit record. Parts 6 and 8 plus the scenario reference describe current
    behavior: required-reference suppression now creates a named blocked
    review, and the browser can acknowledge and approve a sensitive rehome.
    The seed workspace also changed on 2026-09-04: Billing gained its public
    tier plus `meridian-billing-sdk`, `meridian-billing-ledger`, and
    `meridian-billing-models`, so the access-level scenario now targets
    `project.notifications`. Orbit has since retired Application endpoints:
    this record omits the replay's endpoint scenarios, and the rename rows
    describe only their Application changes.

No catalogue proposal in this run was approved. The final proposal was
deliberately rejected after inspection, and later submissions superseded
earlier pending reviews. Neither outcome changes the accepted
catalogue, so every scenario continued to compare against the same baseline.
Both records are immutable, but only supersession is a dead end: an identical
candidate resubmitted after rejection opens a fresh pending review.

| Scenario | Proposal | Submission result | Review observation |
|---|---|---|---|
| Pin placement | `a1f6e161-16cc-455c-bf9f-36d54b0bbe82` | `pending_review` | `meridian-auth` changes from follow to pinned |
| Retier package | `8ef918ba-ca0c-41bc-ad69-7d1680752225` | `pending_review` | `meridian-notify` changes from protected to private |
| Package-group access levels | `8a6c16f0-c98c-45fa-bffc-0b372302e5cb` | `pending_review` | `project.billing` is the only changed package group; estimated stages increase |
| Disable upstream | none | local exit `2` | no review exists; this release accepts only `pypi` |
| Retire package | `d36b31ba-c3a4-4428-9b00-1cd07ef79819` | `pending_review` | accepted side contains `meridian-billing-cli`; proposed side is empty |
| Retire nonempty package group | `c1fc1190-bd8c-4218-b785-7163932cec2f` | blocked / exit `4` | two retire rows, one blocker, and no decision controls |
| Suppress load-bearing dependency | none | `registry_catalog_invalid`, exit `4` | no review exists; the dependency graph is rejected before proposal creation |
| Anchored rename, unresolved | `fc49aac7-5128-43d3-bbf9-e063f27d02d9` | blocked / exit `4` | zero actions, one rename-confirmation blocker, no decision controls |
| Anchored rename, resolved | `b4ea35bb-1cc8-4f78-bb0e-001fcfd5e4cc` | `pending_review` | `notify-worker → notify-dispatcher`, one focused resolution, Application identity retained |
| Unanchored rename | `e6d7a2d4-b255-4f53-b847-3531f6cc96ca` | `pending_review` | create/retire Application rows replace the Application identity |
| Rehome package | `b30f5884-fff2-44b6-a901-0b59b5b66ea9` | `pending_review` | sensitive rehome, failed audience-change condition, physical home changes to `library.config` |
| Unanchored uv Application rename | `3d477d25-192b-4817-a08f-4774b2f9bdf4` | rejected | create/retire rows replace `billing-api` with `billing-service`; no technical topology applied |

## What the live run changed in the documentation

- Rehome submission no longer returns HTTP 500. Proposal creation works.
- At replay time the sensitive review had no UI acknowledgement control. That
  control now exists and Part 8 uses it to approve the bound rehome.
- An unresolved anchored rename deliberately carries zero actions. The rename
  action appears only after supplying the generated resolution.
- `upstream = "none"` is still rejected locally before proposal creation. The
  load-bearing-dependency case now produces a blocked review naming
  `registry_required_reference_suppressed` and its dependency evidence.
- Rejection records the reviewer note without applying the plan, and it closes
  only that review: resubmitting the identical committed candidate opens a new
  pending proposal at exit `8`. A later same-source proposal makes an earlier
  pending review `superseded`, removes its decision controls, and supplies a
  successor link.
- A stale proposal is not reproducible with serial submissions from this one
  source: they supersede each other first. The documented stale lab therefore
  requires a second independently authorized source.
- `registry reviews list` and `reviews open --json` recovered stored review and
  report URLs. `registry reviews show` failed in this run for both an old
  blocked proposal and a newly rejected one with `registry_invalid_response`.
  That was a client response-contract defect and has since been fixed; the
  command now returns the stored report for every proposal, and the raw
  `report_url` in a signed-in browser is a convenience rather than the fallback.
