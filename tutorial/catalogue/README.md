# Catalogue journey — learn topology changes by doing

These optional labs explore changes a growing team makes after onboarding.
Use a **fresh clone and sandbox**, separate from the billing journey: published
artifacts would change the retirement and rehome exercises' preconditions.

## Start the lab track

1. In a new clone, complete [Create your registry](../00-orientation.md). Reuse
   the installed tools; no CI run or publisher credentials are needed for these labs.
2. Follow [Look first](../01-look-first.md), [Add a package](../02-add-a-package.md),
   [Cross a package-group boundary](../03-cross-resource-dependency.md), and
   [Approve and verify](../04-approve-and-verify.md).
3. Complete only [Configure the Product](../product.md#configure-the-product--owner).
   Leave packages unpublished and skip customer acquisition.
4. Continue below in that same cumulative checkout. Each accepted change becomes
   the next step's baseline.

```bash
git status --short
registry status
```

Expect clean Git, converged topology, no pending proposal, and ready provisioning.

## The journey

Work through these pages in order:

| Part | You learn |
|---|---|
| [5 — Make routine topology changes](05-routine-changes.md) | Pins, package access levels, and package-group access levels |
| [6 — Meet the guardrails](06-guardrails-and-retirement.md) | Local refusal, safe retirement, blocked decommission, and invalid dependency graphs |
| [7 — Preserve Application identity](07-identity-and-impact.md) | Anchored renames, rename confirmation, and destructive recreation |
| [8 — Read and approve a sensitive change](08-sensitive-rehome.md) | Rehomes, risk classification, conditions, acknowledgement, and approval |
| [9 — Follow the proposal lifecycle](lifecycle-and-recovery.md) | Lost-link recovery, rejection, resubmission, supersession, and cleanup |

## The journey rhythm

For every successful change:

1. Open the named file and make the documented edit yourself on `main`.
2. Stage and commit the named files.
3. Run `registry topology plan`.
4. Run `registry topology sync`.
5. Open the printed review, inspect the bound diff, and approve it.
6. Run `registry status`; continue only when topology is `converged` and
   provisioning is `ready`. The one exception is Part 7's removal of the
   rename lookup hint: it changes the recorded workspace candidate without
   changing topology, so status reads `repository_ahead` with nothing pending
   until the next accepted change records the new candidate.

`plan` is read-only. `sync` exits `8` while an applicable proposal is waiting
for review; that is an expected handoff, not a crash.

Some lessons deliberately create a candidate that must not be applied. The
page tells you to reject it when decision controls exist, then uses `git
revert` to return the files to the accepted topology. Blocked proposals have
no decision controls; revert the candidate and resync instead. This preserves
both Git history and Orbit's immutable review record while keeping one
cumulative checkout.

!!! warning "Keep Git and Orbit aligned"
    Do not continue from a pending proposal. Approve the successful changes
    and wait for convergence, or follow the documented reject/revert cleanup
    for an experiment. Starting the next edit early makes its diff cumulative
    in ways the walkthrough does not describe.

## Reference material

The journey emphasizes what a user does and learns. These appendices preserve
the exhaustive product detail and historical evidence:

- [Scenario reference](scenario-reference.md) — independent fixture replays,
  raw actions, blockers, impacts, and diagnostics. It is reference material,
  not the main-branch walkthrough.
- [Catalogue coverage](coverage.md) — feature-by-feature status: done,
  partial, stub, broken, or never populated.
- [Verified staging proposals](verified-proposals.md) — immutable proposal
  records inspected during an earlier isolated replay.

## Start

[Part 5 — Make routine topology changes](05-routine-changes.md) begins with a
single package-placement edit and repeats the edit, inspect, commit, plan,
submit, approve, and verify loop with you making every change.
