# Part 2 — Add a package

By the end of this page you have added a package, watched it create a package
group you never declared, and read the resulting review.

## Step 1 — Create the package

Meridian needs a rate-limiting library. Its home follows from where you
put it: `package/library/ratelimit/…` means `library.ratelimit`.

```bash
uv init --lib \
  --name meridian-ratelimit \
  --description "Request throttling helpers" \
  --build-backend hatch \
  --author-from none \
  --no-readme \
  --no-pin-python \
  package/library/ratelimit/meridian-ratelimit
```

`uv init --lib` recognizes the existing workspace and creates the normal
library scaffold: `pyproject.toml`, `src/meridian_ratelimit/__init__.py`, and
the `py.typed` marker. Keep those generated files unchanged. Orbit does not
inspect the sample function in `__init__.py`; the package metadata, lockfile,
and directory path are what matter to topology discovery.

## Step 2 — Update the lockfile

Discovery reads members from `uv.lock`, not from your `pyproject.toml` files.
A new directory that is not in the lock does not exist as far as the registry
is concerned.

```bash
uv lock
```

You should see:

```text
Resolved 12 packages in 46ms
Added meridian-ratelimit v0.1.0
```

## Step 3 — See what it would do

```bash
git add -A && git commit -m "Add meridian-ratelimit shared library"
registry topology plan
```

The plan leads with `2 registry changes are ready for review`. Its change and
status sections say:

```text
Proposed changes
  Add package: meridian-ratelimit
  Add package group: library.ratelimit

Status
  Risk: Routine
  Blockers: None
  Impacts: None
  Required action: Submit this plan for review
```

Two actions from one directory. You declared no package group anywhere — the
path `package/library/ratelimit/…` implied `library.ratelimit`, and the
registry creates it.

`Risk: Routine` means no extra approval ceremony. `Blockers: None` means the
plan is reviewable.

!!! note "Where did `branches` come from?"
    You did not declare `library.ratelimit`, so its enabled tiers were derived —
    here, just the workspace `default_tier`. That is fine for a package group
    with one tier. A group hosting packages at two different tiers must declare
    `branches` explicitly in its technically named resource table, or
    derivation produces a single-tier set and the whole plan fails. The
    catalogue covers this.

## Step 4 — Submit it

```bash
registry topology sync
```

You should see:

```text
Topology change proposal <proposal-uuid>: pending_review; changes=2 blockers=0.

Proposed changes
  Add package: meridian-ratelimit
  Add package group: library.ratelimit
Review: https://<registry-origin>/+app/topology-changes/<proposal-uuid>
```

Your proposal id will differ. Exit code is `8` — review pending — which is a
success, not an error. Scripts can branch on it.

`sync` reports in the same order as `plan`: the decision first, the changes it
bound second, and the review URL last, where it is easy to copy. Add
`--verbose` for the full desired topology, internal identities, and hashes.

## Step 5 — Read the review

Open the full review URL printed by the CLI. Two things to look at now:

**The full technical diff.** Expand it below the decision panel. Because
nothing is removed, it renders as one table headed `+ PROPOSED RESULT ·
NOTHING REMOVED`, folding the unchanged records away and marking the two new
rows with `+`. A proposal that both adds and removes records shows two
tables instead, `− BEFORE` beside `+ PROPOSED RESULT`, with a hatched
placeholder opposite each row that exists on one side only.

**The graph.** Switch between `Proposed` and `Diff`. In `Diff`, the new
package group is marked added. The legend only shows the statuses actually
present, so right now it shows Added and nothing else.

## Step 6 — Approve and converge

Select **Approve registry changes**, then wait for provisioning and confirm:

```bash
registry status
```

```text
Registry status
Connection: verified — <generated-sandbox-name> at https://orbit-staging.home.costanga.com
Repository: ready (binding: local_only)
Topology: converged
Current proposal: none
Provisioning: ready
Next: No command required.
```

Apply this proposal before Part 3. Otherwise the next plan correctly includes
these two still-unapplied actions as well as the dependency change, producing
a combined four-action review and superseding this one.

## What you built

A package and, implicitly, its package group — accepted through a review that
shows both.

## Next

[Part 3 — Cross a package-group boundary](03-cross-resource-dependency.md)
makes the new library depend on another one.
