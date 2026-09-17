# Part 7 — Preserve Application identity

By the end of this page you understand the difference between renaming an
Application and replacing it, and know why Orbit asks for explicit
confirmation.

Continue on `main`. First you will make and reject a destructive rename, then
perform the identity-preserving version and approve it. A final destructive
experiment is also rejected and reverted. Only the anchored rename becomes
part of the cumulative accepted topology.

## Step 0 — Confirm the Part 6 state

```bash
git branch --show-current
git status --short
registry status
```

Expect `main`, no Git status entries, `Topology: converged`, and
`Provisioning: ready`.

## Step 1 — See what an unanchored rename would destroy

`notify-worker` declares its own Application name in
`project/notifications/application/notify-worker/orbit.toml`. Change only:

```toml
name = "notify-worker"
```

to:

```toml
name = "notify-dispatcher"
```

Do not add an identity hint yet.

```bash
git add project/notifications/application/notify-worker/orbit.toml
git commit -m "catalogue: try an Application rename without an identity anchor"
registry topology plan
registry topology sync
```

The plan is applicable and routine, but it contains two actions:

- create Application `notify-dispatcher`;
- retire Application `notify-worker`.

Open the review and compare the removed and proposed Application rows. Without
a link to the old identity, Orbit cannot know that this was intended as a
rename. Approval would replace the Application's UUID even though only its
name changed.

Select **Reject**, optionally noting `Unanchored rename replaces identity.`
Then restore the accepted files and resync:

```bash
git revert --no-edit HEAD
registry topology sync
registry status
```

Continue after topology is `converged` and provisioning is `ready`.

## Step 2 — Preserve the Application's identity

Make the name change again, this time temporarily adding the old name as an
`application_key` lookup hint:

```toml
[registry]
name = "notify-dispatcher"
application_key = "notify-worker"
kind = "worker"
description = "Delivers queued notifications"
```

```bash
git add project/notifications/application/notify-worker/orbit.toml
git commit -m "catalogue: rename notify-worker with an identity anchor"
registry topology plan
```

The desired row now matches an accepted identity, but Orbit will not infer the
rename silently. The plan is blocked with zero actions and one
`registry_rename_confirmation_required` blocker.

Submit once so the exact blocker is preserved in a review:

```bash
registry topology sync
```

Exit `4` includes a review URL. Open it and confirm there are no decision
controls. Then generate the owner-bound resolution Orbit requires:

```bash
RESOLUTIONS_DIR="$(mktemp -d /tmp/orbit-rename-resolutions.XXXXXX)"
RESOLUTIONS_FILE="$RESOLUTIONS_DIR/resolutions.json"
registry topology resolutions-template --output "$RESOLUTIONS_FILE"
```

Inspect `RESOLUTIONS_FILE`. Its rename confirmation should name the accepted
Application UUID and the expected workspace owner. Use that generated document
to plan and submit again:

```bash
registry topology plan --resolutions "$RESOLUTIONS_FILE"
registry topology sync --resolutions "$RESOLUTIONS_FILE"
```

The resolved plan has one `rename application` action and explicitly shows
`notify-worker → notify-dispatcher` on the accepted Application, so its
identity is retained. The blocked review you opened a moment ago is now marked
`superseded`: the resolved submission replaced it, and its blocker stays
readable from the review history.

Open the new pending review, select **Approve registry changes**, and verify:

```bash
registry status
```

The anchor has done its job. Delete only this temporary line from `orbit.toml`:

```toml
application_key = "notify-worker"
```

Commit the cleanup and prove that it has no topology meaning after the rename
is accepted:

```bash
git add project/notifications/application/notify-worker/orbit.toml
git commit -m "catalogue: remove the completed rename anchor"
registry topology plan
registry topology sync
```

`sync` reports that no registry changes are needed. `registry status` then
reads `Topology: repository_ahead` rather than `converged`. Removing the
lookup hint changes the workspace candidate the CLI records, even though the
derived registry topology is unchanged; the accepted candidate still includes
that hint, so status reports the workspace as ahead. No proposal is needed and
nothing waits for approval; the next accepted topology change, Part 8's
rehome, records the new candidate and the status returns to `converged`. The
anchor was a lookup hint, not stored topology.

## Step 3 — Inspect replacement of a uv Application

A uv workspace member takes its Application name from `[project]`, so renaming
the project is the same identity decision. Rename `billing-api` without an
anchor. In `project/billing/application/billing-api/pyproject.toml`, change:

```toml
name = "billing-api"
```

to:

```toml
name = "billing-service"
```

Relock because the uv workspace member's project name changed:

```bash
uv lock
git add -A
git commit -m "catalogue: inspect replacement of the billing Application"
registry topology plan
registry topology sync
```

Expect two actions, as in Step 1: create Application `billing-service` and
retire Application `billing-api`. Approval would allocate a new UUID, and
anything Orbit records against the old identity would not follow it. For
example, removing an Application from the accepted catalog archives its
[image storage](../images.md); the replacement would start without any.

To rename a uv Application safely, use the Step 2 pattern: add the old name as
`application_key = "billing-api"` under `[tool.orbit.registry]` for one commit
and submit the generated rename resolution.

Reject the proposal, then restore both the project file and lockfile:

```bash
git revert --no-edit HEAD
registry topology sync
registry status
```

## Step 4 — Confirm the cumulative state

```bash
git branch --show-current
git status --short
registry status
```

You should be on `main` with a clean tree, ready provisioning, and
`Topology: repository_ahead` from the anchor removal in Step 2. The accepted
Application is now named `notify-dispatcher` with its original identity; both
unanchored rename experiments were rejected and reverted.

## What you learned

A stable display key is not a durable identity. Identity-preserving renames
need both an authored lookup hint and an explicit, owner-bound resolution.
Without them, a small edit becomes a create-and-retire sequence that replaces
the Application's durable identity.

## Next

[Part 8 — Read and approve a sensitive change](08-sensitive-rehome.md) moves a package
between package-group homes and shows how Orbit turns exposure changes into risk
classification, acknowledgement, and approval gates.
