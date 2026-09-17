# Part 5 — Make routine topology changes

By the end of this page you can make ordinary package and package-group edits
yourself and recognize how each appears in an Orbit review.

Work in the same checkout you used for Parts 0–4. Every successful change is
approved on `main`, so each accepted result becomes the baseline for the next
step. You—not a scenario helper—will edit and stage every file, commit every
change, submit every plan, decide every review, and verify convergence.

## Step 0 — Confirm the cumulative starting point

```bash
git status --short
git branch --show-current
registry status
```

Git should print no status entries, the branch should be `main`, and Orbit
should report `Topology: converged`, `Current proposal: none`, and
`Provisioning: ready`.

For each step below, `registry topology sync` exits `8` and prints a review URL.
Open that URL, inspect the stated checkpoint, select **Approve registry
changes**, and then run:

```bash
registry status
```

Continue only after topology is `converged` and provisioning is `ready`.

## Step 1 — Pin a package's placement

Placement normally follows directory shape. Pinning says that this accepted
home should remain fixed even if the directory later moves.

Open `pyproject.toml`. Find the exact member entry for `meridian-auth` and add
`pin = true`:

```toml
[tool.orbit.registry.members.meridian-auth]
tier = "public"
pin = true
```

Commit and submit your edit:

```bash
git add pyproject.toml
git commit -m "catalogue: pin meridian-auth placement"
registry topology plan
registry topology sync
```

Look for one routine `update package` action whose only changed field is
`placement_mode`. Expand **Full technical diff**: because nothing is removed
it is a single `+ PROPOSED RESULT · NOTHING REMOVED` table, and the
`meridian-auth` row is marked modified with its **Pin** column changing from
off to on. Approve it and complete the status checkpoint from Step 0.

## Step 2 — Change an accepted package's tier

Defaults and path rules place new packages; they do not silently retier an
already accepted package. An exact member entry is required.

In `pyproject.toml`, change only the tier in this block:

```toml
[tool.orbit.registry.members.meridian-notify]
tier = "private"
```

```bash
git add pyproject.toml
git commit -m "catalogue: retier meridian-notify"
registry topology plan
registry topology sync
```

The plan contains one routine package update and names only `tier` as changed.
The review shows `meridian-notify` moving from `protected` to `private` while
remaining in the same package group. Approve it and verify convergence.

Because Step 1 is already accepted, it is absent from this focused diff. That
is the value of completing the loop before making the next edit.

## Step 3 — Enable another package-group access level

The technically named `branches` field determines which access-level indexes
Orbit materializes for a package group. In `pyproject.toml`, find
`project.notifications` and add `public` to `branches`:

```toml
[tool.orbit.registry.resources."project.notifications"]
display_name = "Notifications"
branches = ["public", "protected", "private"]
```

```bash
git add pyproject.toml
git commit -m "catalogue: enable the public notifications tier"
registry topology plan
registry topology sync
```

Checkpoint: one routine `update registry_resource` action, with `branches` as
the changed field. The estimated topology size increases because one enabled
tier produces both staging and production indexes. Approve and verify.

## Step 4 — Confirm the new accepted baseline

```bash
git branch --show-current
git status --short
registry status
```

You should still be on `main`, Git should print no status entries, topology
should be `converged`, and provisioning should be `ready`. All three routine
edits are now both committed and accepted; Part 6 starts from this state.

## What you learned

Routine changes can affect different kinds of topology entity, but their review
shape is consistent: a focused action, the exact compared fields, no blockers,
and no additional acceptance gates. You also saw that completing each review
keeps the next diff focused without branches or clones.

## Next

[Part 6 — Meet the guardrails](06-guardrails-and-retirement.md) deliberately
tries changes that stop locally, retire cleanly, or create blocked reviews,
then safely restores `main` whenever a candidate must not be applied.
