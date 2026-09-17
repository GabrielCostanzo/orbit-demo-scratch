# Part 9 — Follow a proposal through its lifecycle

By the end of this page you can recover a lost review, reject and resubmit a
candidate, recognize a superseded proposal, and return `main` to the accepted
Part 8 topology without deleting immutable history.

Both lifecycle candidates are experiments. You will not approve them; after
observing their review states, you will reject and revert them.

## Step 1 — Confirm the accepted starting point

```bash
git branch --show-current
git status --short
registry status
```

Expect `main`, no Git status entries, `Topology: converged`, `Current proposal:
none`, and `Provisioning: ready`. This is the cumulative topology from Parts
5–8, including the accepted Billing CLI retirement, anchored Application
rename, and telemetry rehome.

## Keep the exit codes nearby

`registry topology sync` uses distinct exits for review state. In a shell with
`set -e`, temporarily handle the result instead of treating every non-zero
value as a crash.

| Exit | Meaning | What to do |
|---|---|---|
| `0` | applied or already converged | Verify `converged` and `ready` |
| `2` | local/configuration refusal | Fix the workspace; no proposal exists |
| `3` | credential rejected | Reconnect this checkout with `registry init` |
| `4` | blocked/conflict | Open the stored review when a proposal URL was returned |
| `5` | transport/protocol/remote failure | Retry only after checking the origin and CLI compatibility |
| `8` | pending review | Expected for an applicable submission; open the URL |
| `9` | superseded | Follow the printed successor URL or submit from the current commit |
| `10` | stale | Regenerate from current accepted state |
| `11` | reserved for `rejected` | Nothing to do—`sync` does not produce it; see Step 4 |

Exit `3` commonly appears after staging is wiped and reseeded underneath a
checkout that worked earlier:

```text
registry: The registry credential was not accepted. Refresh it or reconnect with registry init. (registry_authentication_failed)
```

Run `registry init`. It reconnects the checkout, or explains that the sandbox
is gone and starts a reviewed replacement.

## Step 2 — Submit a routine candidate on `main`

Open the root `pyproject.toml`. Add `pin = true` to the existing
`meridian-config` entry:

```toml
[tool.orbit.registry.members.meridian-config]
tier = "public"
pin = true
```

Commit and submit it:

```bash
git add pyproject.toml
git commit -m "catalogue: exercise proposal lifecycle"
LIFECYCLE_CANDIDATE_COMMIT="$(git rev-parse HEAD)"
registry topology plan
registry topology sync
```

The plan has one routine package update whose changed field is
`placement_mode`. Exit `8` means the proposal is pending. Copy its proposal ID
from the printed URL, but then pretend the rest of the terminal output is gone.

## Step 3 — Recover the review link

Losing terminal output does not lose the proposal. List immutable review
records for this checkout:

```bash
registry reviews list
registry reviews list --status pending_review
registry reviews list --json
```

The JSON form contains `proposal_id`, `status`, `review_url`, `report_url`, and
`successor_review_url`. Assign the pending pin proposal's ID so later commands
are easy to copy:

```bash
PIN_PROPOSAL_ID="<proposal-id>"
registry reviews open "$PIN_PROPOSAL_ID"
```

For scripts, `--json` prints the URL and opens no browser:

```bash
registry reviews open "$PIN_PROPOSAL_ID" --json
```

It reports `"status": "printed"`, so a caller can distinguish a printed URL
from one handed to a browser.

Read the immutable report without a browser:

```bash
registry reviews show "$PIN_PROPOSAL_ID" --json
```

This works for pending, blocked, applied, rejected, and superseded proposals.
The document includes actions, blockers, impacts, evidence, acceptance gates,
hashes, provenance, and warning codes. The review UI links to the same raw
report from **Verification**, inside **Technical risk and sizing details**.

## Step 4 — Reject and resubmit the same commit

1. Open the pending review recovered in Step 3 and confirm its bound plan and
   diff.
2. Enter `Catalogue lifecycle exercise: reject without applying.` in the
   optional review note.
3. Select **Reject**.
4. Run `registry topology sync` again without editing or committing anything.

After rejection the first review becomes `rejected`, its decision controls
disappear, and the note and reviewer appear in **Review overview**. Nothing is
applied.

The identical committed candidate returns as a **new pending proposal** with
its own ID and review URL, and `sync` exits `8`. Update the variable to the new
proposal ID:

```bash
registry topology sync
PIN_PROPOSAL_ID="<new-proposal-id>"
```

Rejection ends one review, not the proposed change. The rejected record remains
immutable history, while the same files may open a new conversation.

Exit `11` is reserved for a rejected proposal, but `sync` no longer has a way
to return it because resubmission creates the new review above. You can still
see `11` from `registry init` if a reviewer rejects the tenant-create proposal
itself.

## Step 5 — Supersede it with a newer `main` commit

Leave the resubmitted pin proposal pending. In `pyproject.toml`, change the
accepted Billing core tier:

```toml
[tool.orbit.registry.members.meridian-billing-core]
tier = "private"
```

Commit and submit the newer cumulative candidate:

```bash
git add pyproject.toml
git commit -m "catalogue: supersede the lifecycle proposal"
registry topology plan
registry topology sync
```

The successor contains two actions because neither experiment is accepted:
the still-authored `meridian-config` pin plus the new Billing core retier. The
new same-source proposal becomes current and the resubmitted pin proposal
becomes `superseded`.

Copy the successor proposal ID, then reopen the older review:

```bash
SUCCESSOR_PROPOSAL_ID="<successor-proposal-id>"
registry reviews open "$PIN_PROPOSAL_ID"
```

The older review's banner says a newer proposal replaced it, decision controls
are absent, and **Open current review** follows the successor. The stored
lifecycle row names both `superseded_by_id` and `successor_review_url`:

```bash
registry reviews list --json
registry reviews show "$PIN_PROPOSAL_ID" --json
```

No clone or competing branch is needed. The second commit on `main` is enough
to show that only the newest candidate from source `meridian/monorepo` can be
current. Rejection closes a conversation you may restart; supersession says
the source has already moved past that candidate.

## Advanced lab — Understand the stale boundary

A serial second submission from this repository makes the first proposal
`superseded`, not `stale`. A real stale decision needs the accepted registry
revision to move after the report was generated without the proposal being
replaced first. That requires a second independently authorized source or a
concurrency test harness.

Do not manufacture that condition in a tenant you care about. In a disposable
two-source lab, the sequence is:

1. Source A submits proposal A and leaves it pending.
2. Independently bound source B submits and applies a compatible change.
3. Reopen or attempt to decide proposal A.
4. Confirm the stale banner, absent decision controls, and exit `10` when the
   candidate is observed again.
5. Rebase source A on the newly accepted topology, commit, and submit a new
   report.

The main journey does not create a second source binding, so this boundary is
documented but not claimed as a one-source reproducible exercise.

## Step 6 — Reject the successor and restore accepted state

Open the current successor and select **Reject**:

```bash
registry reviews open "$SUCCESSOR_PROPOSAL_ID"
```

Now revert the newer retier commit, then the original pin commit. These are new
history entries on `main`; they do not erase either experiment:

```bash
git revert --no-edit HEAD
git revert --no-edit "$LIFECYCLE_CANDIDATE_COMMIT"
registry topology plan
registry topology sync
registry status
```

The final plan and sync should find no topology change. Confirm `Topology:
converged`, `Current proposal: none`, and `Provisioning: ready`.

```bash
git branch --show-current
git status --short
```

You should still be on `main`, with no Git status entries. Rejected and
superseded reviews remain queryable; there are no exercise clones or branches
to clean up.

## What you learned

Proposal records are immutable, but their lifecycle meanings differ. Rejection
ends one review and permits a new conversation about the same commit.
Supersession means the source has moved on to a newer commit. A lost URL is
recoverable from review history, and the final reverts restore the accepted
topology without rewriting Git history.

## Topology journey complete

You have now exercised the topology authoring loop from routine edits through
blocked, invalid, identity-sensitive, and sensitive changes, then recovered
and closed the resulting reviews. Use the [scenario
reference](scenario-reference.md) for isolated diagnostics and [catalogue
coverage](coverage.md) to see which product surfaces are live-verified,
partial, or still stubs.

## Next

[Part 10 — Connect an uploader and publish to staging](../10-connect-and-publish.md)
keeps this accepted topology and begins the artifact journey with two packages
in different package groups.
