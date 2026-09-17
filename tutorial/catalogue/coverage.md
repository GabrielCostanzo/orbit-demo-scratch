# Catalogue coverage

Historical coverage of the earlier topology/release walkthrough. Part numbers
and live replay claims below refer to that version, not the new billing path.
Use the [current journey](../../README.md) for instructions. The new helper and
invoice code require their own CI run; these records are not evidence for it.

Every user-facing feature of the topology-change report, and where it is
covered. This is the index; it is deliberately complete, so anything missing
from the tutorial is visible rather than silently absent.

The entity and blocker tables retain exact contract identifiers such as
`registry_resource` and `registry_reference`. The web app and the narrative
tutorial call those concepts **package groups** and **dependencies**.

**Status legend**

- **Done** — written, and its output captured from a live registry.
- **Partial** — the supported portion is live-verified; the named boundary is
  not claimed as complete.
- **Stub** — the trigger is known and stated here, but not yet executed or
  written up. Treat the description as intent, not verified behaviour.
- **Broken** — reachable, but currently fails. Documented as such.
- **Never** — exists in the UI but no server path populates it.

---

## Action operations

| Operation | Trigger | Status |
|---|---|---|
| `create` | New member directory + `uv lock`; new package-group key; new Application | **Done** — Part 2 and the unanchored Application rename |
| `update` | Any compared field changes: tier, pin, branches, `depends_on`, catalog settings | **Done** — pin, retier, and package-group access-level entries |
| `retire` | Delete a directory, or the last dependency pointing to a package group | **Done** — Retire a package |
| `rehome` | A member's resolved home changes | **Partial** — sensitive submission is live-verified; Part 8 covers the implemented acknowledgement and approval flow, whose post-fix staging replay is still pending |
| `rename` | Move a package-group configuration table / rename a distribution / rename an Application, keeping the accepted identity | **Done** — Rename an Application, with and without the `application_key` anchor; needs a `rename` resolution via `resolutions-template`; renders `previous_key → key` in the diff |
| `adopt` | Re-declare an entity the registry holds with no owner | **Stub** — appendix; needs a second workspace |
| `take_ownership` | Declare an entity another source owns | **Stub** — appendix |
| `detach` | Remove an entity but keep it in the registry, unowned | **Stub** — never inferred; must be hand-written. Package groups, packages, and Applications can be detached |

## Entities

| Entity | Status |
|---|---|
| `registry_resource` (package group) | **Done** — create (Part 2), update access levels, retire blocker |
| `package` | **Done** — create, update tier/pin, retire |
| `registry_reference` (dependency) | **Done** — create (Part 3), suppression failure |
| `application` | **Done** — Rename an Application (anchored and unanchored). Both declaration modes exist in the repo and neither authors a UUID |
| `product` | **Not a topology entity** — the dedicated Product journey uses the web-owned promotion workflow |
| `catalog` | **Locked** — a custom `layer_order` and `upstream = "none"` both stop at local validation; no catalog change is authorable in this release |

## Classifications

| Class | Trigger | Status |
|---|---|---|
| `routine` | Everything not below | **Done** — every proposal-producing entry except the rehome |
| `sensitive` | A rehome crossing layer, kind, tier, or audience | **Partial** — classification, condition, and gates are live-verified; the required acknowledgement UI is implemented and documented, with a post-fix staging replay pending |
| `bulk` | More than 10 rehomes, or ≥3 rehomes affecting >25% of members | **Stub** — needs a live mass-move replay; the browser has a report-bound bulk confirmation control |
| `migration_required` | Rehoming a package that has uploaded artifacts | **Stub** — needs a publish first; the plan is never applicable |

## Proposal statuses

| Status | Trigger | Status |
|---|---|---|
| `pending_review` | An applicable plan with actions | **Done** — Part 2 |
| `applied` | Approved | **Done** — Part 4 |
| `converged` | Accepted technical topology matches the committed candidate | **Done** — Part 0 status, Part 1's no-op plan, and the Product journey's post-promotion check |
| `blocked` | Any blocker present; no approve button exists | **Done** — retire-a-package-group blocker |
| `rejected` | Reviewer rejects | **Done** — two routine proposals rejected with notes; no technical topology applied. Renegotiable: resubmitting the identical candidate opens a new pending review at exit `8` |
| `stale` | The registry moved after the report was generated | **Partial** — banner and recovery are documented, but a live replay needs a second independent source; serial same-source submissions become superseded |
| `superseded` | A newer same-source proposal replaces this one | **Done** — old review loses decisions and links to the successor |

## Review screen elements

| Element | Status |
|---|---|
| Status chip, bound plan hash | **Done** — Part 4 |
| Split diff: two tables, four columns | **Done** — Part 2 |
| Pin column on/off | **Done** — Pin a member |
| Void rows opposite a create or retire | **Done** — Part 2 |
| Gutter signs, per-entity icons, per-cell tints | **Stub** — visible in any diff; not called out step by step |
| Unchanged-record fold (`⋯ N unchanged records`) | **Stub** — appears on any change to this repo; expanding restores both sides |
| Rename rendering `previous_key → key` | **Done** — Rename an Application |
| Row selection syncing graph and diff | **Stub** — click a node or edge to select its changes |
| Topology graph: `Proposed` vs `Diff` views | **Done** — Part 2 |
| Edge sets: `Dependencies` vs `Packages` | **Done** — Part 3 |
| Internal-edges toggle | **Done** — Product journey Step 5 reveals the Billing chain on the Project's technical page |
| Change legend (Added / Modified / Removed) | **Done** — Part 2 |
| Dependency-provenance legend | **Stub** — hidden while every edge is `inferred`; needs an authored `add_references` edge |
| Repository, branch, and short commit in the heading | **Done** — Part 4 |
| Decision summary: outcome and decision signals | **Done** — Part 4 |
| Verification (inside Technical risk and sizing details): plan/candidate/desired/report hashes, raw report link | **Done** — Part 4 |
| Review note panel | **Done** — captured on rejected catalogue proposals |
| Safety and placement panel | **Done** — submitted rehome review shows `sensitive` and `registry rehome audience change` |
| Logical and physical changes panel | **Partial** — key renames covered by the Application rename; the "physical stage identity is retained" note is package-group-only and no longer shown for Applications |
| Estimated topology size | **Partial** — Package groups and Stages populate; Bases and Closure never do |
| Decision controls, plan/report hash binding | **Done** — Part 4 |
| History/recovery: list older, open successor, Report JSON | **Done** — list and successor are live, the raw-report link exists, and CLI `reviews show` returns the stored report |

## Banners

| Banner | Trigger | Status |
|---|---|---|
| Dirty checkout | Submitted from an uncommitted tree | **Stub** — the CLI refuses first, so this needs another client |
| Superseded | A newer proposal exists | **Done** — captured with disabled decisions and current-review link |
| Stale | Registry moved after the report | **Partial** — requires the two-source lab described in lifecycle and recovery |
| Tenant creation boundary | A `tenant_create` proposal | **Done** — Part 0 submits it with `registry init`, reviews the atomic creation boundary, approves it, and waits for provisioning |
| Report/proposal mismatch | Stored report does not match | **Never expected** — an integrity failure, not an authoring outcome |
| Delegated review required | Source binding uses a repository policy | **Stub** — needs a delegated binding |

## Blockers

Covered in the journey: `registry_resource_decommission_requires_workflow`
and `registry_rename_confirmation_required` are live-verified;
`registry_required_reference_suppressed` is implemented and documented, with
a post-fix staging replay pending.

**Stub** — everything else, grouped by what causes them:

- **Ownership** — `registry_adoption_required`, `registry_take_ownership_required`,
  `registry_resolution_owner_mismatch`, `registry_product_ownership_conflict`
  (appendix).
- **Rename** — `registry_rename_destination_collision` remains a stub.
- **Graph** — `registry_reference_self`, `registry_reference_project_target`,
  `registry_reference_rank_violation`, `registry_reference_cycle_explicit`,
  `registry_reference_tier_unsatisfiable`, `registry_reference_unknown_target`.
- **Dependency** — `registry_dependency_tier_violation` (depend on a more
  private package) and `registry_dependency_unreachable`. Suppressing a
  dependency-derived reference is covered separately by
  `registry_required_reference_suppressed`, with exact member evidence.
- **Identity** — `registry_resource_identity_hint_unknown` and its package and
  Application equivalents; `registry_package_name_conflict`. An authored
  `application_id` that matches no accepted row is a blocker, which is why a
  *new* Application must not carry an invented UUID.
- **Decommission** — `registry_package_decommission_requires_workflow`, with
  evidence `live_artifacts` / `release_candidates` / `dependent_members`.
- **Rehome** — `registry_sensitive_rehome_exact_assignment_required`,
  `registry_package_rehome_requires_migration`.
- **Policy** — `registry_upstream_policy_conflict`,
  `registry_inference_version_change_requires_preview`.
- **Limits** — resource, node, edge, Product, composition-link,
  reference-depth, bases-per-stage, and effective-SRO ceilings.

## Warnings and acceptance gates

| Item | Trigger | Status |
|---|---|---|
| `registry_upstream_policy_change` | Flipping `upstream` | **Unavailable** — current client contract accepts only `pypi`, so no proposal exists |
| `registry_rehome_audience_change` | A rehome across audiences | **Partial** — the condition and gate are live-verified; Part 8 covers the implemented acknowledgement checkbox and bound approval, with a post-fix staging replay pending |
| Acceptance gates (7) | Sensitive, bulk, and migration classes | **Partial** — three are shown in the submitted rehome output |

## CLI surface

| Command | Status |
|---|---|
| `topology validate` | **Done** — Part 1 |
| `topology plan` | **Done** — throughout |
| `topology sync` | **Done** — Part 2; decision, proposed changes, then the review URL by default, with `--verbose` for desired topology and hashes |
| `status` | **Done** — Part 0 verifies the connection and reports Git/binding readiness, topology, active proposal, provisioning, and one next command |
| `init` / `context show` | **Done** — Part 0 covers the CLI/server contract handshake, device authorization, immutable review, approval, readiness, `{workspace_slug}-sandbox-{hex8}` naming, OS-keychain storage, idempotent reconnect, clone context inheritance, verified context and active-proposal inspection, automatic resume, and vanished-sandbox replacement without production recreation |
| `topology create` | **Advanced handoff** — writes a tenant document for an integration that intentionally owns submission; it is not the interactive tutorial path |
| `topology resolutions-template` | **Done** — generated rename confirmation, resubmitted, and reviewed with one focused resolution |
| `reviews list` | **Done** — returns immutable lifecycle rows, report URLs, and successor URLs |
| `reviews open` | **Done** — normal form opens the stored review; `--json` prints it with `"status": "printed"` and opens no browser |
| `reviews show` | **Done** — returns the stored immutable report for every proposal, superseded included; the old `registry_invalid_response` failure was a client contract defect and is fixed |
| `connect` / `publish` | **Partial** — Part 10 is a complete guided flow and the exact artifact set is locally verified; its staging upload still needs a captured live replay |
| `promote` | **Partial** — Part 11 covers immutable candidates, real CI evidence, human decisions, and production polling; a live CI-backed replay is not yet recorded here |
| `configure uv` / `device status` / `device logout` | **Partial** — Part 12 covers the OS-keyring consumer flow and the two-package install is locally verified; a live gateway replay is not yet recorded here |
| `release` (Launchpad loop) | **Done** — Part 13 replayed end to end on Meridian (2026-08-27) against a disposable registry: reader-path sandbox init (device sign-in + reviewed create), Launchpad 0.1.0→0.2.0, the metadata-only status detail, one `registry release` to the approval gate, real-SPA approval, wheel+sdist in production, and a keyring-authenticated gateway install of exactly 0.2.0 |

## Never populated

No server path writes these; the UI renders its empty state permanently.

- Entitlement impact
- Product-closure impact
- Warnings in the summary panel
- Estimated Bases and Product closure links
