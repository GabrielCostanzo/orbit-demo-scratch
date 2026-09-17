# Part 8 — Read and approve a sensitive change

By the end of this page you can read a sensitive topology report, distinguish
its technical action from its approval conditions, acknowledge the risk, and
approve the exact bound change.

Continue on `main`. This package rehome is accepted and becomes the cumulative
baseline for Part 9.

## Step 0 — Confirm the Part 7 state

```bash
git branch --show-current
git status --short
registry status
```

Expect `main`, no Git status entries, `Provisioning: ready`, and
`Topology: repository_ahead`: Part 7 ended by removing the rename lookup hint,
which changed the recorded workspace candidate without changing topology. The
rehome below records the new candidate.

## Step 1 — Assign a package to a different home

Directory shape places `meridian-telemetry` in `library.observability`. An
exact member entry can deliberately override that inferred home.

Open `pyproject.toml` and use the technically named `resource` field to assign
the existing member to the `library.config` package group:

```toml
[tool.orbit.registry.members.meridian-telemetry]
tier = "private"
resource = "library.config"
```

Commit and preview it:

```bash
git add pyproject.toml
git commit -m "catalogue: rehome meridian-telemetry"
registry topology plan
```

Unlike the applicable proposals in Part 5, this plan is `class=sensitive`. It
contains one `rehome package meridian-telemetry` action whose changed field is
`home_resource_id`.

## Step 2 — Read the acceptance gates

The sensitive plan carries three gates, which the review presents as approval
requirements:

```text
committed_exact_assignment
entitlement_admin_permission
registry_rehome_audience_change_acknowledgment
```

They answer questions separate from “what row changes?”:

- Was the destination assigned explicitly in a committed repository state?
- Does the reviewer hold authority for the exposure boundary being crossed?
- Did the reviewer acknowledge the audience change rather than overlooking it?

This is why the plan remains technically applicable while its risk is no
longer routine.

## Step 3 — Submit and inspect the review

```bash
registry topology sync
```

Submission exits `8` and prints the review URL. Open it and inspect:

1. The accepted and proposed package-group homes in the full technical diff.
2. The `sensitive` classification in the safety panel.
3. The failed `registry rehome audience change` condition.
4. The physical rehome row.
5. The acceptance gates bound to the decision.

The enabled approval button is not sufficient by itself. In **Required
acknowledgements**, select:

> I understand that this rehome changes the effective audience and may alter
> Product entitlement behavior.

The acknowledgement is sent with the exact proposal, plan hash, and report
hash. Select **Approve registry changes** only after that checkbox is
selected.

## Step 4 — Verify the accepted rehome

```bash
registry status
```

Continue only when topology is `converged` and provisioning is `ready`. In the
review, the status should be `applied`; `meridian-telemetry` now belongs to
`library.config` even though its source directory remains beneath
`library/observability`.

## What you learned

Sensitive changes add authority and acknowledgement requirements without
changing the underlying technical action. The review makes those requirements
explicit and binds the acknowledgement to the exact report a human inspected.

## Next

[Part 9 — Follow the proposal lifecycle](lifecycle-and-recovery.md) creates
routine candidates on the same `main` history to recover a lost link, reject
and reopen a conversation, supersede an older proposal, and finish with the
accepted Part 8 topology unchanged.
