# Part 3 — Cross a package-group boundary

By the end of this page you understand the single most important mapping in
the system: **a dependency between package groups makes the required packages
available to the depending group.** Orbit implements that relationship using
index bases, but you do not need to manage those bases yourself.

## Step 1 — Depend on another library

`meridian-telemetry` needs settings loading. From the workspace root, add
`meridian-config` with uv:

```bash
uv add --package meridian-telemetry --no-sync meridian-config
```

The root workspace already contains both packages. `--package` selects the
member whose dependencies uv should edit, and `--no-sync` skips installing the
whole workspace while still updating `pyproject.toml` and `uv.lock`.

Open `package/library/observability/meridian-telemetry/pyproject.toml` and see
what uv generated:

```toml
dependencies = [
    "meridian-config",
]

[tool.uv.sources]
meridian-config = { workspace = true }
```

Both halves matter. The ordinary dependency survives into published package
metadata. Because uv recognized `meridian-config` as another root-workspace
member, it also wrote `[tool.uv.sources]`; that makes this a workspace edge,
and only workspace edges become topology.

```bash
git add package/library/observability/meridian-telemetry/pyproject.toml uv.lock
git commit -m "meridian-telemetry depends on meridian-config"
```

## Step 2 — Plan it

```bash
registry topology plan
```

You should see:

```text
2 registry changes are ready for review.

Proposed changes
  Update package: meridian-telemetry
    Changed: depends on
  Add dependency: library.observability → library.config

Status
  Risk: Routine
  Blockers: None
  Impacts: None
  Required action: Submit this plan for review
```

The stable assertions are two changes, no blockers, an update to
`meridian-telemetry.depends_on`, and one dependency from the
`library.observability` package group to `library.config`.

One dependency, two actions:

- **Update package** — the package's own `depends_on` changed.
- **Add dependency** — a new edge from `library.observability` to
  `library.config`. The diagnostic `--verbose` view uses the contract terms
  `registry_reference` and `resource UUID`; the default view translates those
  implementation identifiers back to the package-group names you recognize.

That dependency is the whole point. Orbit adds the required base to the
`library.observability` production indexes, so anything installing telemetry
can also resolve config.

## Step 3 — Notice what does *not* create a group dependency

Nothing to edit here — this one is a thought exercise about an edge the repo
already has. `meridian-billing-cli` depends on `meridian-billing-core`, and
both live in `project.billing`.

Ask what that edge is worth to the registry, then check Part 1's plan: it
counted **`Dependencies between groups: 3`**, and this is not one of them. A
same-group dependency contributes to the depending package's `depends_on` but
creates **no dependency between groups**. Packages in one package group already
resolve each other, so there is no boundary to cross and no base to add.

That is the whole distinction. Step 1's edit was interesting only because it
crossed a boundary.

## Step 4 — See it in the graph

Submit and open the review:

```bash
registry topology sync
```

Open the full review URL printed by the CLI.

In the relationship graph, switch the level from `Packages` to
`Group references`. The new edge appears between the two package-group boxes,
marked added. (The **What changed** summary above the graph counts the same
edges as **Group references**, distinct from the `depends_on` edges the
`Packages` level draws between individual packages.)

Below the canvas is the **dependency provenance legend**. Your edge is
`inferred` — derived from a dependency. The legend distinguishes that from
`explicit` (authored by hand) and `accepted` (already in the catalog). Right
now every edge is inferred, so the legend stays hidden; it only appears once
provenances differ. The catalogue shows you how to author an explicit one.

## What you built

A dependency between package groups, derived entirely from a Python dependency
you declared for ordinary application reasons.

## Next

[Part 4 — Approve and verify](04-approve-and-verify.md) completes the loop.
