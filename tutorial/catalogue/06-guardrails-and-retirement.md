# Part 6 — Meet the guardrails

By the end of this page you can tell four outcomes apart: a local contract
refusal, a blocked decommission, a blocked invalid graph that identifies the
exact dependency you broke, and an ordinary retirement.

Stay on `main`. The unsafe experiments are committed so Orbit can inspect their
provenance, then reverted so the files agree with accepted topology. The final
ordinary retirement is approved; besides advancing the tutorial, that newer
proposal supersedes the last blocked review and leaves the source fully clean.

## Step 0 — Confirm the Part 5 state

```bash
git branch --show-current
git status --short
registry status
```

Expect `main`, no Git status entries, `Topology: converged`, and
`Provisioning: ready`.

## Step 1 — Cross a local contract boundary

The repository schema contains an `upstream` setting, but this release accepts
only `pypi`. In `pyproject.toml`, change:

```toml
upstream = "pypi"
```

to:

```toml
upstream = "none"
```

Commit the experiment and ask the local client to plan it:

```bash
git add pyproject.toml
git commit -m "catalogue: try to disable the upstream"
registry topology plan
```

The CLI exits `2` and explains that `upstream = "none"` is not available in
this release. The refusal happens before a valid candidate can be planned, so
there is nothing to submit and no review to recover.

Restore the supported configuration without rewriting history:

```bash
git revert --no-edit HEAD
registry topology plan
```

The plan should now say the workspace is converged. The lesson is not that you
need a workaround; the installed client contract defines the authoring
surface.

## Step 2 — Try to retire a nonempty package group

`library.ratelimit` was inferred from the package created in Part 2. It has no
explicit, technically named resource table to delete, so removing its last
package also proposes retiring the package group itself.

```bash
git rm \
  package/library/ratelimit/meridian-ratelimit/pyproject.toml \
  package/library/ratelimit/meridian-ratelimit/src/meridian_ratelimit/__init__.py \
  package/library/ratelimit/meridian-ratelimit/src/meridian_ratelimit/py.typed
uv lock
git add -A
git commit -m "catalogue: try to retire the ratelimit package group"
registry topology plan
```

Read the result before submitting. It should contain:

- `retire package meridian-ratelimit`;
- `retire registry_resource library.ratelimit`;
- blocker `registry_resource_decommission_requires_workflow`;
- evidence `package_homes`.

Now submit the blocked report:

```bash
registry topology sync
```

`sync` exits `4` and prints a review URL. Open it. Both retire rows are visible,
the blocker explains what still occupies the package group, and there are no
decision controls. `registry status` classifies the state as decommission
required and directs you to a dedicated decommission workflow; it does not
recommend an ownership-resolution template.

This is a durable safety record. There is no resolution file that can waive
decommission evidence. Because the tutorial does not perform a decommission,
restore the package and lockfile:

```bash
git revert --no-edit HEAD
registry topology sync
```

The files and desired topology are converged again. Orbit may retain the
different blocked proposal as the current immutable review until the next
candidate supersedes it; that does not mean the blocked deletion was applied.

## Step 3 — Suppress a load-bearing dependency

Part 3 showed that a dependency between package groups makes packages in the
target group available. Now suppress the only group dependency through which
`meridian-billing-core` can reach `meridian-auth`.

In the existing, technically named `project.billing` resource table in
`pyproject.toml`, add:

```toml
remove_references = ["library.auth"]
```

Then commit, plan, and submit:

```bash
git add pyproject.toml
git commit -m "catalogue: suppress the billing auth dependency"
registry topology plan
registry topology sync
```

This candidate supersedes the earlier blocked deletion. The plan and new
blocked review identify the graph problem directly:

```text
blocker registry_reference registry_required_reference_suppressed project.billing->library.auth
  evidence: member=meridian-billing-core dependency=meridian-auth
```

`sync` exits `4` and prints a review URL. Open it and verify that there are no
decision controls: no reviewer choice can make an unreachable dependency safe.
Restore the dependency configuration:

```bash
git revert --no-edit HEAD
registry topology sync
```

The files and desired topology are converged. The blocked review can remain
current until the successful proposal in Step 4 supersedes it.

## Step 4 — Retire an unused package

`meridian-billing-cli` has no uploads, release candidates, or dependent
workspace members, and no access option sells it: the Product journey's
**Billing engine** sells `meridian-billing-core`. Removing it is therefore an
ordinary change.

Delete its two tracked files:

```bash
git rm \
  project/billing/package/meridian-billing-cli/pyproject.toml \
  project/billing/package/meridian-billing-cli/src/meridian_billing_cli/__init__.py
```

Open the root `pyproject.toml` and remove this exact member entry:

```toml
[tool.orbit.registry.members.meridian-billing-cli]
tier = "protected"
```

Relock, commit the complete deletion, and submit it:

```bash
uv lock
git add -A
git commit -m "catalogue: retire the unused billing CLI"
registry topology plan
registry topology sync
```

Checkpoint: one routine `retire package meridian-billing-cli` action, no
blockers, and a pending review. Because a record is removed, the full
technical diff now splits into `− BEFORE` and `+ PROPOSED RESULT`: the package
sits on the left with a hatched placeholder opposite it on the right. This new
proposal also makes the blocked dependency review `superseded`.

Open the pending review, select **Approve registry changes**, and wait for the
cumulative state to settle:

```bash
registry status
```

Continue only when topology is `converged`, `Current proposal` is `none`, and
provisioning is `ready`.

## Compare the outcomes

| Exercise | Exit | Proposal exists? | Meaning |
|---|---:|---|---|
| Unsupported upstream | `2` | No | The local authoring contract rejects the configuration |
| Retire nonempty package group | `4` | Yes, blocked | Decommission needs a dedicated workflow, not a resolution override |
| Suppress required dependency | `4` | Yes, blocked | The named package dependency would become unreachable |
| Retire unused package | `8` | Yes, then applied | The change is reviewable, routine, and now accepted |

Do not treat exit code alone as the diagnosis. Read whether a proposal URL was
returned, then inspect its blockers and evidence.

## Step 5 — Confirm the cumulative state

```bash
git branch --show-current
git status --short
registry status
```

You should be on `main` with a clean tree, no current proposal, converged
topology, and ready provisioning. The Billing CLI retirement is accepted; both
blocked experiments have been reverted and superseded.

## What you learned

Orbit separates authoring validation, graph validity, proposal safety, and
review decisions. A non-zero exit can preserve a useful immutable blocked
review, while a local contract refusal creates no review at all. A later valid
candidate supersedes blocked work without erasing its history.

## Next

[Part 7 — Preserve Application identity](07-identity-and-impact.md)
shows why an apparently simple rename can either preserve an Application or
destroy and recreate its identity.
