# Scenario reference — one edit, one submitted review

This is the exhaustive companion to the guided
[catalogue journey](README.md). Start with Part 5 if you want to perform the
exercises in learning order; use this page when you need the exact raw action,
blocker, impact, or current product limitation for one scenario.

This appendix is deliberately different from the user journey. Each entry is
an independent fixture replay from the converged end-of-Part-4 state, so a
fresh local clone keeps its raw expected diff reproducible. Do not interleave
these commands with Parts 5–9, which are cumulative on `main` and have the user
author, approve, reject, or revert every change.

```bash
CATALOGUE_PARENT="$(mktemp -d /tmp/orbit-catalogue.XXXXXX)"
git clone --no-local . "$CATALOGUE_PARENT/workspace"
cd "$CATALOGUE_PARENT/workspace"

python3 tutorial/catalogue/scenario.py pin
git diff --check
git diff
git add -A
git commit -m "catalogue: exercise pin"

registry topology plan --verbose
registry topology sync
```

`--no-local` is intentional: on macOS, `/tmp` can be a different filesystem,
and Git's local hard-link optimization then fails with `Operation not
permitted`.

The clone needs no `registry init`. Registry context is keyed by the workspace's
`source_key` and origin, not by the folder, so a clone made by the same user
inherits the connected checkout's context and keychain credential; `registry
init` there would just report **This checkout is already connected**.

Replace `pin` with the scenario key named in each entry. The helper refuses a
dirty checkout, or one missing `meridian-ratelimit` from Part 2 and the baseline
files it edits. It relocks automatically for the two deletion scenarios and for
the unanchored uv Application rename.

`plan` is optional and read-only. The catalogue uses `--verbose` because its
assertions name raw actions, acceptance gates, and blocker codes; the main
tutorial uses the compact default. `sync` takes the same flag for the same
reason — its default output is the decision, a short proposed-change list, and
the review URL last, while `--verbose` adds the desired topology, internal
identities, and hashes the entries below quote.

`sync` is the step that actually submits. For an applicable proposal it prints
a review URL and exits `8` while review is pending. Open that URL and inspect
the technical diff, safety panel, impacts, blockers, and decision controls. Do not
approve if you want to keep using this same accepted baseline: the next
submitted scenario can supersede the prior pending proposal without changing
the catalogue.

One scenario is refused locally before a proposal can exist, and three produce
a blocked review with no decision controls. Those outcomes are part of the
demonstration and are identified inline.

The original blocks were replayed against Orbit staging on 2026-08-15. The
[verified proposal log](verified-proposals.md) records those proposal IDs and
what was visible then. The required-reference blocker and sensitive
acknowledgement descriptions incorporate later implemented fixes; their fresh
staging replay is still pending.

Hashes, UUIDs, and estimated counts in the captured output are examples from
one compatible run. Compare the classification, action kinds, changed fields,
warnings, blockers, and relationships; do not compare run-specific
identifiers literally.

## Scenario keys

| Entry | Helper key | Submission outcome |
|---|---|---|
| Pin placement | `pin` | pending review |
| Retier package | `retier` | pending review |
| Package-group access levels | `resource-tiers` | pending review |
| Disable upstream | `upstream-policy` | local validation refusal; no proposal |
| Retire package | `retire-package` | pending review |
| Retire nonempty package group | `retire-resource` | blocked review |
| Suppress load-bearing dependency | `suppress-reference` | blocked review with dependency evidence |
| Anchored Application rename | `rename-anchored` | blocked, then pending with a resolution |
| Unanchored Application rename | `rename-unanchored` | pending review |
| Unanchored uv Application rename | `rename-uv-application-unanchored` | pending review |
| Rehome package | `rehome-package` | sensitive pending review |

---

## Pin a member's placement

Placement normally follows the directory. Pinning freezes it, so moving the
directory later produces no rehome.

```toml
[tool.orbit.registry.members.meridian-auth]
tier = "public"
pin = true
```

```text
Registry plan 2b6695896167: applicable; class=routine actions=1 blockers=0 impacts=0
  action update package meridian-auth class=routine
    changed fields: placement_mode
```

In the review's technical diff, the **Pin** column changes from off to on. It is
the only column whose meaning is not a value you typed.

---

## Retier a package

```toml
[tool.orbit.registry.members.meridian-notify]
tier = "private"
```

```text
Registry plan 3226a2ef3546: applicable; class=routine actions=1 blockers=0 impacts=0
  action update package meridian-notify class=routine
    changed fields: tier
```

Note what does **not** work: changing `default_tier`, or a path rule's `tier`,
has no effect on a package the registry has already accepted. Only an exact
member entry retiers it. The new tier must be enabled for its home package
group in `branches`, or the plan fails.

---

## Change a package group's enabled access levels

```toml
[tool.orbit.registry.resources."project.notifications"]
display_name = "Notifications"
branches = ["public", "protected", "private"]
```

```text
Registry plan 5a94db65c928: applicable; class=routine actions=1 blockers=0 impacts=0
  action update registry_resource project.notifications class=routine
    changed fields: branches
```

Each enabled tier materializes a staging and a production index, so this one
line creates two more indexes.

---

## Promote a Project to a Product

The main walkthrough is the dedicated
[Product journey](../product-promotion.md). The Project already exists because
it was inferred from `project/billing/`. Open **Projects**, hover **Billing**,
select **Promote to product**, and confirm. Orbit allocates the Product UUID,
derives its slug, and initializes its draft presentation from the accepted
Project package group.

This is a business action, not a helper scenario: it creates no Git diff,
topology plan action, proposal, or review. Product identity, Project binding,
presentation, and lifecycle belong to the web app; Project metadata remains
technical topology.

---

## Change the tenant's upstream policy

Scenario key: `upstream-policy`.

```toml
[tool.orbit.registry]
upstream = "none"
```

The current release refuses this before planning or submission:

```text
workspace_registry_config_invalid: upstream = "none" is not available in this release;
the only supported value is "pypi"
```

The CLI exits `2` and no proposal or review URL is created. There is no client
workaround: keep `upstream = "pypi"` until the registry exposes another
supported policy. This entry remains useful because it distinguishes a local
contract boundary from a blocked server proposal.

---

## Retire a package

Scenario key: `retire-package`. The helper removes the directory, removes its
now-unused exact member entry, and relocks:

```text
Registry plan 0ce641e5f832: applicable; class=routine actions=1 blockers=0 impacts=0
  action retire package meridian-billing-cli class=routine
```

This one is clean because nothing depends on it and it has no uploads. A
package with published artifacts, release candidates, or dependent members is
**blocked** instead, with `registry_package_decommission_requires_workflow`
and evidence naming which of those applies. A blocked proposal has no approve
button at all.

---

## Retire a package group that is not empty

Scenario key: `retire-resource`.

`library.ratelimit` is inferred from the package added in Part 2, so it has no
explicit, technically named resource table to delete. Removing
`meridian-ratelimit` and relocking retires both the package and its inferred
package group:

```text
Registry plan 1eaf4e8b4612: blocked; class=routine actions=2 blockers=1 impacts=0
  action retire package meridian-ratelimit class=routine
  action retire registry_resource library.ratelimit class=routine
  blocker registry_resource registry_resource_decommission_requires_workflow library.ratelimit
    evidence: package_homes
```

`sync` still creates an immutable blocked review. It exits `4`; the UI shows
both removed rows, one blocker, and no decision controls.

For other package groups the evidence list can name:

`package_homes`, `application_homes`,
`resource_references`, `structural_products`, `active_grants`,
`live_artifacts`, `release_candidates`. This is the most informative blocker
in the system. Read the evidence rather than guessing. There is no resolution
document for decommission evidence; migrate or archive the named contents in a
separately authorized workflow first.

---

## Suppress a dependency that is load-bearing

Scenario key: `suppress-reference`.

`remove_references` is the technical setting that deletes a derived dependency
edge. Suppress one that a package still needs and Orbit blocks the candidate
with exact evidence:

```toml
[tool.orbit.registry.resources."project.billing"]
remove_references = ["library.auth"]
```

```text
Registry plan <plan-hash>: blocked; class=routine actions=0 blockers=1 impacts=0
  blocker registry_reference registry_required_reference_suppressed project.billing->library.auth
    evidence: member=meridian-billing-core dependency=meridian-auth
```

`sync` exits `4` and creates an immutable blocked review. The review names the
source and target package groups plus the package dependency that needs the
edge; there are no decision controls. Restore the group dependency or change
the dependency graph so the package remains reachable.

---

## Rename an Application, keeping its identity

Scenario key: `rename-anchored`.

This is the scenario the `application_key` anchor exists for, and the only one
in this catalogue where a line you add is meant to be deleted again.

`notify-worker` declares its own name, so renaming it is a one-line edit in
`project/notifications/application/notify-worker/orbit.toml`. Do **only** this,
and commit:

```toml
[registry]
name = "notify-dispatcher"
application_key = "notify-worker"   # the OLD name -- lookup only, this commit
kind = "worker"
```

```text
Registry plan b55ff87e1301: blocked; class=routine actions=0 blockers=1 impacts=0
  blocker application registry_rename_confirmation_required notify-dispatcher
```

A rename is never inferred silently — it always demands an explicit
resolution. The unresolved desired state deliberately preserves the accepted
Application, so it has zero actions. `sync` creates a blocked review with one
blocker and no decision controls.

Generate the exact owner-bound confirmation and submit again:

```bash
RESOLUTIONS_DIR="$(mktemp -d /tmp/orbit-rename-resolutions.XXXXXX)"
RESOLUTIONS_FILE="$RESOLUTIONS_DIR/resolutions.json"
registry topology resolutions-template \
  --output "$RESOLUTIONS_FILE"

registry topology plan \
  --verbose \
  --resolutions "$RESOLUTIONS_FILE"

registry topology sync \
  --resolutions "$RESOLUTIONS_FILE"
```

`resolutions-template` requires its output path not to exist, so the example
creates a temporary directory and writes a new file inside it. Inspect the JSON:
the generated resolution must name the accepted Application UUID and expected
workspace owner.

With that resolution, the submitted plan is:

```text
Registry plan f12325a6c35e: applicable; class=routine actions=1 blockers=0 impacts=0
  action rename application notify-dispatcher class=routine
    rename notify-worker -> notify-dispatcher
    changed fields: application_key, name
```

The review renders `notify-worker → notify-dispatcher` on the accepted
Application and reports one focused resolution. The anchor does not skip
confirmation; it decides something earlier and more important: **whether the
registry finds the accepted row at all.**

The separate `rename-unanchored` scenario drops the anchor and plans as a
*different* change:

```text
Registry plan <plan-hash>: applicable; class=routine actions=2 blockers=0 impacts=0
  action create application notify-dispatcher class=routine
  action retire application notify-worker class=routine
```

Without the anchor the registry has no way to connect the new name to the old
row, so it destroys and recreates the Application under a new UUID. Note this
second plan is `applicable`: nothing stops you approving it.

The `rename-uv-application-unanchored` variant performs the same
identity-destroying rename against the uv member `billing-api`, changing its
`[project]` name to `billing-service`. It relocks the workspace and produces
the same create and retire pair for that Application.

**Then delete the anchor.** It is a lookup hint, never stored state, so the
next commit produces no diff and costs no second confirmation:

```text
Workspace topology: converged. No action is required.
```

That no-diff result holds only if you approved the rename first — the anchor
becomes redundant precisely because the registry now knows the Application as
`notify-dispatcher`, so deleting it while the proposal is still pending leaves
an ordinary unanchored rename and re-plans the two-action destroy-and-recreate
shown above. This is therefore the one reference entry that asks you to
approve. Run it only in an isolated tenant you are willing to move forward, or
follow the cumulative Part 7 journey instead.

---

## Rehome a package — acknowledge and approve the sensitive move

Scenario key: `rehome-package`.

Move a package to a different package group with an exact member entry:

```toml
[tool.orbit.registry.members.meridian-telemetry]
tier = "private"
resource = "library.config"
```

It **plans** correctly, and this is the only scenario here that is not
`routine`:

```text
Registry plan 33f430bb99c5: applicable; class=sensitive actions=1 blockers=0 impacts=0
  action rehome package meridian-telemetry class=sensitive
    changed fields: home_resource_id
  acceptance gates: committed_exact_assignment, entitlement_admin_permission, registry_rehome_audience_change_acknowledgment
```

`class=sensitive` means the change moves a package between homes with
different exposure, so it demands extra authority. The acceptance gates are
what a reviewer must satisfy.

`sync` now succeeds and returns a normal pending-review URL. The review shows
the accepted and proposed homes, `sensitive`, the failed
`registry rehome audience change` condition, and the physical rehome row.

The review's **Required acknowledgements** section exposes the audience-change
checkbox. Selecting it enables **Approve registry changes** and sends
`registry_rehome_audience_change` with the exact bound report. The server still
refuses an unacknowledged sensitive decision.

---

## What is never populated

These areas of the review read empty on an ordinary workspace change. Do not
go looking for them:

- **Entitlement impact** — no current topology plan emits one.
- **Product-closure impact** — only a placement inference-version upgrade
  emits one.
- **Warnings** in the summary panel.
- **Bases** and **Product closure links** in the estimated-size panel.
