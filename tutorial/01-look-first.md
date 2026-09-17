# Part 1 — Look before you touch

By the end of this page you can read your workspace's topology without changing
the accepted registry, and you have seen the clean-commit boundary stop an
uncommitted submission.

## Step 1 — Validate locally

`validate` runs entirely on your machine. It never contacts the registry, so
it is the fastest way to catch an authoring mistake.

```bash
registry topology validate --workspace .
```

You should see:

```text
Topology is valid: source=meridian/monorepo candidate=<candidate-hash> package-groups=6 packages=10 applications=2
```

Read that line carefully, because you never declared most of it:

- **package-groups=6** — but `pyproject.toml` declares only **five**
  `[tool.orbit.registry.resources]` tables. The sixth group, `library.search`,
  was inferred from `package/library/search/`. Those technically named tables
  configure package groups; they do not bring the groups into existence.
- **packages=10** — discovered from `uv.lock`, not from any list you wrote.
- **applications=2** — `billing-api` and `notify-worker`, found two different
  ways (Part 2 of the catalogue covers the difference). Neither declares
  **a single UUID**. Open
  `project/billing/application/billing-api/pyproject.toml`: the whole registry
  declaration is `kind = "service"`. The name comes from `[project]`, the home
  from the directory path, and durable identity is allocated by the server when
  the proposal is accepted.
- **candidate=&lt;candidate-hash&gt;** — a hash of the *meaning* of this
  workspace under the installed CLI contract. It is the same on machines
  using the same compatible CLI and checkout. Product administration is not
  part of that technical meaning; server-allocated UUIDs never are.

## Step 2 — Ask the registry what would change

`plan` sends the candidate to the registry and returns the actions it would
take. It changes nothing.

```bash
registry topology plan
```

The default view leads with the decision and groups the workspace by package
group.
The useful parts of this unchanged plan look like this:

```text
Topology plan complete

No registry changes are needed.
This was a preview; nothing was changed.

Workspace detected
  Package groups: 6
  Packages: 10
  Applications: 2
  Dependencies between groups: 3
  External packages: PyPI fallback enabled

Organization
  library.search — tiers: private
    Package: meridian-search (private)
  project.billing — tiers: public, protected, private
    Packages: meridian-billing-cli (protected), meridian-billing-core (protected), meridian-billing-ledger (protected), meridian-billing-models (protected), meridian-billing-sdk (public)
    Application: billing-api

Placement
  All 12 workspace members were placed from the recognized directory layout.

Dependencies
  library.search → library.auth
  project.billing → library.auth
  project.notifications → library.config

Status
  Risk: Routine
  Blockers: None
  Impacts: None
  Required action: None
```

The placement sentence is the point of this page. Every one of those homes
came from the **directory path**. No file names a package group for these
members. If you move a directory, the home moves with it. The **Dependencies**
section lists the three group-to-group edges behind `Dependencies between
groups: 3`; Part 3 adds a fourth. `External packages: PyPI fallback enabled`
restates the workspace's `upstream = "pypi"` setting.

The default keeps hashes, UUIDs, generated index estimates, and individual
inference paths out of the way. To inspect the exact evidence for every member,
rerun the preview in diagnostic mode:

```bash
registry topology plan --verbose
```

That view includes lines such as:

```text
  meridian-search -> library.search reason=recognized_layout path=package/library/search/meridian-search
  billing-api -> project.billing reason=recognized_layout path=project/billing/application/billing-api
```

`meridian-search -> library.search` is the sharpest case: nothing in
`pyproject.toml` mentions `library.search` at all. The directory created the
package group, and the technically named `resources` table you *would* write
only exists to configure a group that already exists.

The two Applications are grouped under their package groups on the same terms
as the packages. They are there because of where they sit, not because they
announced themselves with an identifier.

Package-group metadata is still useful. A technically named resource table's
`display_name` and `description` supply the human-readable labels shown by the
API, navigation, and relationship graph; its `branches` and dependency
settings control how the group is exposed.

## Step 3 — Confirm the clean-checkout boundary

Temporarily add a comment above Billing's resource table in the root
`pyproject.toml`:

```toml
# Local clean-checkout test; remove after the next command.
[tool.orbit.registry.resources."project.billing"]
branches = ["public", "protected", "private"]
```

```bash
registry topology sync
```

You should see:

```text
Workspace topology: local_uncommitted. Commit or discard workspace changes before registry status or sync.
```

The registry only accepts topology bound to a commit. There is no way to
submit "what is on my disk right now".

Restore the temporary edit before continuing:

```bash
git restore -- pyproject.toml
git status --short
```

Git should print no status entries. The accepted registry and Git history were
never changed.

## What you built

No topology change — deliberately. You can now read placement evidence and
recognize the clean-commit boundary before making the first real change.

## Next

[Part 2 — Add a package](02-add-a-package.md) makes the first real change.
