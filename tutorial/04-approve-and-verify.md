# Part 4 — Approve and verify

By the end of this page you have approved a change, watched it converge, and
returned the workspace to `converged`.

## Step 1 — Read the review before deciding

Open the review path from Part 3. Work top-down:

**Heading and source.** The status, repository, branch, and short commit are
kept together at the top. The decision still binds the complete plan hash; if
the registry moved underneath you, approval is refused rather than applied to
something you did not read.

If the submitter had an uncommitted tree, a prominent banner says so and tells
you not to approve. The CLI refuses first, so you would only see this from
another client.

**Decision summary.** The proposal outcome and the few signals that affect the
decision. Read verification literally: for a manually reviewed workspace,
commit provenance is caller-declared and *not server-verified*. The registry
records what it was told.

**What changed.** The concise summary counts package groups, packages, group
references, and Applications. Expand **Full technical diff** when
you need the exact accepted and proposed records.

**Technical risk and sizing details.** Collapsed at the bottom: the safe-follow
classification, acceptance gates, entitlement and Product-closure impact, the
estimated topology size, and a **Verification** block with the plan,
candidate, desired, and report hashes plus a link to the raw JSON report.

## Step 2 — Approve

Type an optional note and select **Approve registry changes**.

Two things are checked that you cannot see: the plan hash and the report hash
must both still match. That is what makes "I approved this" mean one specific
document rather than "whatever the workspace looks like now".

The status chip turns green and reads `applied`, and your note appears under
**Review note** at the bottom of the page.

## Step 3 — Verify convergence

```bash
registry status
```

You should see:

```text
Registry status
Connection: verified — <generated-sandbox-name> at https://orbit-staging.home.costanga.com
Repository: ready (binding: local_only)
Topology: converged
Current proposal: none
Provisioning: ready
Next: No command required.
```

`applied` means the registry accepted it. `ready` means it materialized into
real indexes. Both matter — a change can be accepted and still be mid-flight.

## Step 4 — Look at what it built

No additional browser action is required for this step: the `applied` review
plus `converged` and `ready` above are the user-flow verification. The current
package-group page shows its stages and packages but does not list materialized
base names.

Your new dependency became an index base. The production indexes for
`library.observability` now list the matching `library.config` production
index among their bases, so a client installing from telemetry resolves config
without any extra configuration.

The rule that decides *which* auth index: the nearest tier at or below the one
you are installing from. A `public` index can only ever base on another
`public` index — it can never reach a more private one. That constraint is
structural, not a policy check.

## What you built

The full loop: edit, commit, plan, submit, review, approve, converge. Every
later scenario is a variation on it.

## Next

Return to the [optional labs](catalogue/README.md#start-the-lab-track) to
configure Billing's Product, then continue through routine and sensitive changes.
