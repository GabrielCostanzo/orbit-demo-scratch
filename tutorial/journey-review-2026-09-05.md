# Orbit journey review — main journey completed

Reviewed on 2026-09-05 using Chrome through the browser extension, against https://orbit-staging.home.costanga.com/+app.

The walkthrough resumed after the user requested that findings be recorded. The user then directed the review to continue through recoverable issues and pause only when manual user action is required.

Starting material: `/Users/costanga98/workspace/dev/orbit-demo`, commit `be5abb8` (`tutorial: enable fork workflows and explain repository_ahead by candidate`). A clean disposable clone is preserved at `/private/tmp/orbit-journey.KRpGqi/meridian`. Exercise code stays in the disposable clone; only the findings report and its evidence are added to the original repository.

Chrome opened an existing session signed in as `demo-owner`. No password entry was needed, so the login form itself was not tested. The landing page selected the existing `stage2-clean-room-primary` registry; this is not the fresh Meridian registry the tutorial creates.

## Current coverage

Parts 0–13 and the Product/storefront journey have completed along the main owner-account tutorial path. Genuine GitHub Actions runs passed for the exact published audit and release commits. Auth 0.1.0, search 0.1.0, and auth 0.2.0 each reached immutable production in the disposable staging tenant. A fresh consumer environment downloaded both 0.1.0 packages through the single consumer gateway with cache disabled, imported both, then downloaded and imported auth 0.2.0. The device connection is revoked and its local credential/configuration removed. Both audit release tokens are now revoked, and their local keychain entries and profile metadata have been removed with absence verified.

The connected checkout is clean at `a4db804` on `codex/orbit-journey-release-2026-09-05`. The user explicitly approved the two audit branches and the two auth tags pushed to GitHub; GitHub main was not changed. Exercise edits remain in disposable checkouts. The source demo repository contains only audit documentation/evidence changes.

Scope limits: the browser reused the existing owner login, so the login form and non-staff purchase/license-acceptance flow were not tested. Optional imagery, entitlement-impact fixtures, and the two-source stale lab were not run. Installer setup used the CLI's isolated `configure_home` destination instead of writing the existing user uv/pip files. Historical checkpoints below record earlier pauses and have been superseded by later verified outcomes.

## Prioritized findings

P1 indicates a documented main-path step that fails as written. P2 indicates a substantial clarity or recovery gap; P3 is a smaller presentation inconsistency. The detailed observations and recoveries follow in the chronological evidence log.

| Priority | Area | Observed friction | Recommended change |
| --- | --- | --- | --- |
| P1 | Part 13, Step 2 | Pinned Launchpad 0.1.1 rejects `--ci none`; the flag explanation is also incorrect. | Test the exact pinned binary, correct the command and flag guidance, and verify which executable is on PATH. |
| P1 | Part 13, Step 8 | `uv add` fails because Part 12 never creates a `pyproject.toml`. | Keep the existing `uv pip install` approach or explicitly initialize a consumer project. |
| P2 | Parts 12 → 13 | Cleanup revokes credentials the next part requires. | Move cleanup to the end or add an explicit continuation branch. |
| P2 | Release verification | Tutorial asks for a manifest comparison against JSON that omits the manifest/digests/review URL. | Return candidate identity, artifact digests and a review link in `registry release --json`. |
| P2 | Installer entry points | Home/Quickstart route to `registry.read` personal tokens; publishing/tutorial use device connections. | Use a consistent device-connection setup route and credential vocabulary. |
| P2 | Credential handoff | Staging write-token dialog shows direct-install and environment-secret instructions; device dialog lacks Copy/setup commands; token inventory omits the actual group. | Tailor instructions to operations, surface keychain login/setup, and show the selected group in inventory. |
| P2 | Promotion guidance | Publishing suggests `--wait` before teaching CI submission; CI run details are plain text. | Explain the pending gate, show the evidence command, and link to the provider run. |
| P2 | Release layout | Four identifier cards stay side by side in a narrow content pane, pushing evidence/approval below the fold. | Stack or use two columns, shorten copyable hashes, and prioritize the next required action. |
| P2 | Availability wording | “Available”/“included,” awaiting-release counts and install CTAs conflate entitlement with installability. | Show access and release status separately at package level; tailor empty-state actions. |
| P2 | Product setup | Unexplained repeated-resource counts and “Requirements are optional” conflict with the protected selection. | Name the counting unit, preserve bundle details, and tailor requirements to the selection. |
| P2 | License template | Unresolved year, holder and evaluation-period placeholders can be saved as an immutable license. | Collect required template values or visibly block an unfinished template. |
| P2 | Blocked reviews | “Cannot be submitted” contradicts saved blocked reviews; useful recovery is buried and sometimes points to the wrong next step. | Say “cannot be applied,” lead with the blocker and provide its specific recovery command. |
| P2 | Retirements | Old endpoints lose parent and accepted metadata in the Before view. | Preserve the full previous hierarchy and audience/description for review. |
| P2 | CLI initialization | Config-storage permission failure is reported as workspace unreadable. | Report the actual configuration path/boundary and supported recovery. |
| P2 | Sandbox guidance | Tutorial says clones inherit source context; installed CLI sandboxes are checkout-local. | Explain the binding model and the need to initialize another clone. |
| P3 | Loading/status | Transient empty/unconfigured messages, stale provisioning labels and unlabeled historical review links suggest incorrect current states. | Use loading states and distinguish current state from historical reports. |
| P3 | Naming/navigation | Broad “placement change,” group-reference/dependency labels, retained rehome links, and generic docs labeled API reference require interpretation. | Match labels to the actual change and destination. |
| P3 | Token table layout | Reaching the status/actions columns scrolls token names out of the narrow pane. | Keep the token name column visible while reviewing status or actions. |
| P3 | Local release cleanup | Part 12 says profile files contain revoked secrets; current profiles store credentials in OS keychain, and CLI has no profile logout command. | Document both metadata and keychain cleanup or supply a supported profile-removal command. |

## First failure: initialization reports the wrong cause

Part 0, Step 3 was attempted from the clean disposable clone with the installed CLI:

```bash
registry init --origin https://orbit-staging.home.costanga.com --sandbox --restart --no-open --timeout 600
```

`--no-open` keeps browser interaction in the Chrome extension. The bounded timeout does not affect this immediate failure.

Observed result, exit code 2:

```text
registry: The workspace could not be read. (workspace_unavailable)
```

Expected: print a one-time device sign-in code and URL, then wait for browser authorization.

Evidence:

- The clone is clean and contains committed `pyproject.toml` and `uv.lock` files.
- `registry --version` reports `registry-cli 0.1.0a1`, contract `stage6-v1`, and the required `0.1.0a1` dependency versions.
- The local, read-only `registry topology validate --workspace .` succeeds: source `meridian/monorepo`, candidate `e0923efad627`, 6 package groups, 10 packages, 2 applications.
- A diagnostic replay captured `PermissionError`, errno 1, for `/Users/costanga98/.config/registry`, starting in the installed `registry_cli/profiles.py:309`. The exception then reaches the generic `workspace_unavailable` handler.

The trigger is the execution environment's filesystem restriction on the CLI configuration directory. This does not establish a staging backend defect. The confirmed CLI clarity defect is that a configuration write failure is described as a workspace read failure, directing the user toward the wrong repair.

Suggested behavior: report a configuration-storage error with the affected directory, explain that initialization has not reached sign-in, and provide a supported recovery action. For example: “Cannot write registry configuration to <path>. Check directory permissions or select a writable REGISTRY_CONFIG_DIR, then rerun registry init.”

The journey did not reach device sign-in, proposal submission, registry creation, or provisioning.

## Initial landing-page clarity and friction notes

1. **Entitlement and release availability need a clearer distinction.** The hero says “1 package included with membership”; the Authentication card exposes “1 available to you”; farther down, “Your access 0” says “No released packages are available yet,” and `orbit-demo-auth` appears under “Awaiting release.” These can describe different concepts correctly, but a new user can read the first two as installable now. Use “Included with membership · awaiting first release” near the package and reserve “available to install” for released artifacts.
2. **The primary actions do not reflect the empty state.** “Set up installation” is prominent while no package is released, and “Browse Products” is offered with 0 Products. Add a short explanation that installation can be prepared now and releases are pending. Omit or soften the Products action until there is something to browse. These are presentation recommendations; the actions were not followed.

## Resume checkpoint: topology core completed

- Findings were copied into the demo repository as `tutorial/journey-review-2026-09-05.md`.
- The execution environment uses `REGISTRY_CONFIG_DIR=/private/tmp/orbit-journey.KRpGqi/registry-config` and `UV_CACHE_DIR=/private/tmp/orbit-journey.KRpGqi/uv-cache`. CLI calls requiring network and keychain access run with tool-approved expanded permissions. These changes isolate this audit from existing registry context and address the test environment restrictions; they are not product fixes.
- Device sign-in, expected consent, review, approval, provisioning, and verified CLI context succeeded. Created sandbox `meridian-sandbox-0c938f9e`, tenant `4c3e5227-11e3-4099-9f5c-8a5c19a305c3`, creation proposal `4c9c6638-f6fd-405d-aa30-f895905b5793`.
- Part 1: inspected placement evidence and verified the documented `local_uncommitted` refusal. The temporary edit was restored.
- Part 2: added ratelimit in commit `5ecd7f3`; proposal `2272000e-cb69-4e95-8a0b-ece0f18c2345` contained exactly the package and group additions. Approved in Chrome; status converged and provisioning ready.
- Parts 3–4: added the telemetry/configuration dependency in commit `ded5b07`; proposal `54437eda-6e03-4696-8e8e-5dd9e28ad494` contained exactly the package update and inferred group reference. Inspected the graph and technical risk/verification details in Chrome, approved, and verified convergence.
- Positive flow: review summaries, clean-commit refusal, source labels, status output, and post-creation onboarding all gave usable next steps.
- Minor terminology note: the plan calls cross-group links “Dependencies,” while the review uses “Group references.” The tutorial explains the equivalence, but matching labels would reduce translation work.

Next: Product promotion and storefront journey.

## Product checkpoint: live Billing storefront

Promoted Billing to draft Product `e6285a59-f283-4336-93b2-6e093d40a455`. Configured registry summary, description, story, capability, compatibility, FAQ, tutorial link and documentation URL, verifying revisions 1–3. Filtering and FAQ expansion worked. Created Billing engine, selected only core, verified the bundled ledger/models and shared auth, created and attached the tutorial evaluation license, supplied Product presentation, activated, and verified the live result. The Product advertises SDK + core + ledger + models (4); auth and unsold CLI stay off the storefront. The home shows 3 membership packages and Billing with “1 included · 3 unlockable with 1 add-on.” Staff access is explicit. Technical views showed all six packages, application endpoints, internal edges, group resolution, and public-only SDK. CLI status remains converged and ready.

Additional findings:

- **Convergence feedback remains stale on the applied review.** After CLI verified convergence and ready provisioning, the browser review still said “2 changes were approved and queued for convergence” and “Approved and queued for provisioning.” Give the review a current provisioning result or a direct status link.
- **Unexplained access counts.** “Contents and access 13” counts candidate resources and repeated dependency rows, not 13 unique packages. The final option review says “What users can use (1)” for a bundle that advertises 3 protected packages. Label the units and preserve the dependency summary in the final review.
- **Requirement guidance contradicts the selected resource.** For the selected protected core, the Requirements step starts “Requirements are optional,” then explains they are required for protected feeds, and a warning prevents Continue. Tailor the lead sentence to the current selection.
- **Unresolved license-template placeholders are accepted.** Following the tutorial literally creates an immutable Evaluation License containing `[year]`, `[copyright holder]`, and `[evaluation period]`. The UI offers no fill-in prompts and the tutorial says to keep the generated text. Collect those values before creation or clearly mark the template as incomplete. This test created a fictional sandbox license; no member accepted it.
- **Generic documentation is labeled “API reference.”** The editor asks only for Documentation URL, but the home renders its destination as “API reference — Modules, endpoints and reference.” Use “Documentation” or let the owner select the label.
- **Product installation wording overstates readiness.** The live Product says “All 4 packages are available to you,” shows a public-tier feed URL, and offers “Get free access” even to staff. The release explanation is inside a collapsed fold, where “Releases 0 · 1 awaiting release” describes fewer packages than the four displayed. Put release readiness alongside each package, tailor the CTA for existing access, and make the feed's scope clear. The public feed's suitability for installing protected packages has not been tested.
- **Transient load states can read as final conclusions.** On initial draft load, the Product briefly showed “This Product is not available yet” / “owner has not configured how members can use it,” before resolving to 1 included package. A loading state would avoid this temporary false conclusion.

The owner account follows the tutorial's Staff access variant. A non-staff license-acceptance flow has not been tested with these owner credentials. Optional imagery and stale-revision concurrency were not exercised.

## Catalogue checkpoint and required approval

Part 5 Step 1 succeeded: commit `3e7c335`, proposal `c62fd89d-be5c-4a25-a818-e5e3e4c5920a`, authentication placement pinned and provisioning verified ready. Step 2 succeeded: commit `e6ce1d7`, proposal `b9d5d4cc-1651-435c-a549-3cbdd2c4f966`, notification package changed protected → private and provisioning verified ready. A vanished Chrome audit tab was recovered by opening the saved pending-review URL in the same Chrome browser; no proposal was lost.

Step 3 is fully prepared at commit `51f0ba6`: only the Notifications package-group `branches` change from `[protected, private]` to `[public, protected, private]`. `meridian-notify` remains private. The immutable report shows one routine `registry_resource` update, no blockers, no impacts, no required acknowledgement, zero artifact inventory, and no promotion inventory. The sandbox's sole member is the owner account. Orbit's public production tier is for active tenant members, rather than anonymous Internet users.

Review URL: https://orbit-staging.home.costanga.com/+app/topology-changes/70d3c956-393e-4a57-8e3a-54c5ae8eaca6

Automatic approval review rejected the browser's Approve action because adding a public tier is an access-policy change whose recipient/scope was not explicitly authorized. After additional read-only checks established the empty artifact inventory, unchanged private package, and membership-only access model, the same action was rejected again for the same authorization reason. No bypass or alternate approval mechanism was used. The proposal remains pending; explicit user authorization is required before retrying it.

The effect to authorize is enabling the Notifications public tier for future public releases accessible to active registry members in this disposable sandbox. It does not retier the existing private notification package.

Additional catalogue clarity note: both a package tier change and a package-group tier addition are summarized as “1 placement change.” The word suggests movement between groups; use “access tier change” for these two cases and reserve placement for pin/home changes.

Remaining limitations: installation and promotion checks are still ahead; no production-release or successful consumer-install claim is made. The tutorial's later CI-backed promotion requires a GitHub-visible fork/run, which has not been set up in this local-only checkout.

## Resume checkpoint: Parts 5–7 completed

The user explicitly authorized proposal `70d3c956-393e-4a57-8e3a-54c5ae8eaca6`; it was approved in Chrome and verified converged/ready. Remaining Part 5 endpoint edits were approved and provisioned: console audience `3187f43a-7695-43e2-ad79-c3bcb52d750c` and health description `835dd8ab-141e-457e-8abf-9afc5bfcf832`.

Part 6: `upstream=none` produced the expected local refusal, then was reverted. Nonempty group retirement `49b44192-7a52-4641-954d-64a444226ee9` and suppressed required dependency `3a57b831-03c9-481f-811c-8885568d5e57` produced blocked reviews with no decision controls. Both experiments were reverted. Unused Billing CLI retirement `bfb84a1c-2f6f-467d-bfb1-b1d219de1a9a` was approved; topology converged and provisioning became ready.

Part 7: unanchored worker rename `8bfb51e6-6f70-4387-ba40-bac40cc21a19` showed four actions and was rejected/reverted. Anchored rename first produced blocker `43e9e778-a3e3-487c-9fa8-8ed4b55bb968`; an owner-bound resolutions template targeted Application `f2c37058-84f1-4150-89c5-bf39dd0e1780`. Resolved rename `67942ecc-f1f3-4f30-88f6-e39e32721afe` preserved that Application and its endpoint and was approved. Removing the completed anchor gave the documented metadata-only-ahead state, now clarified in CLI output as “converged (metadata-only ahead — nothing to do).” Reporting endpoint retirement `5ffb0586-d949-4b60-afd1-c771bcc037da` and full Billing Application replacement `1ac56520-f515-4849-bc46-ce3c5a2c1440` were inspected, rejected and reverted. This followed the main path without the optional entitlement-impact fixture, so impact counts were zero.

New findings:

- **Blocked does not mean unsubmitable.** `plan` says “This plan is blocked and cannot be submitted,” but `sync` deliberately creates the useful immutable blocked review. Say “cannot be approved/applied” and identify how to save or inspect the report.
- **Blocked-review recovery is buried and underspecified.** The meaningful blocker appears after the large graph and technical folds. “registry resource decommission requires workflow — package_homes” gives no package count or workflow link. The rename blocker says to “correct the workspace” although the intended next step is `registry topology resolutions-template`. Lead with the blocker, name the affected package/endpoint, and supply the actual recovery command or destination.
- **Converged sync output links to an obsolete blocked review without labeling it.** After reverting each blocked experiment, sync said “converged” but printed the old blocked Review URL. Label that link as historical, and explain whether any action is still required.
- **Retirement diffs omit the accepted endpoint context.** The endpoint-only “Before” pane showed just `reports` under ENDPOINTS, without `billing-api`, Revenue reports, audience, or description. The unanchored Application replacements likewise separated retired endpoint keys from their old parent while fully showing the new tree. Keep retired endpoint rows nested and display their complete accepted metadata; otherwise an owner cannot confidently review which similarly named endpoint is being removed.

Current Part 8 proposal: `628a0115-cd25-4f7c-8e2a-d29bc0cf44a9`, commit `287dee1`, one explicit private telemetry rehome from Observability to Configuration with sensitive-review gates. It is pending and has not yet been approved at this checkpoint.

## Part 8 approval handoff

The sensitive rehome review was inspected in Chrome, including the complete diff, physical placement, risk classification and acceptance gates. It moves `meridian-telemetry` from `library.observability` to `library.config`; the package remains private. The report shows no entitlement or Product-closure impacts. Approval was correctly disabled before the audience-change acknowledgement and enabled after selecting it. This improves on the tutorial wording that refers to an enabled approval button before acknowledgement.

Automatic approval review rejected the final Approve action because the user had authorized the walkthrough and the earlier Notifications proposal, but not this exact sensitive rehome. The action changes resource home and effective audience under an entitlement-admin gate. No alternate approval mechanism or bypass was attempted. The proposal remains pending; existing provisioning remains ready.

Action awaiting user authorization: approve proposal `628a0115-cd25-4f7c-8e2a-d29bc0cf44a9` in sandbox `meridian-sandbox-0c938f9e`, moving private telemetry from Observability to Configuration and accepting the report's possible audience/entitlement effects.

Review: https://orbit-staging.home.costanga.com/+app/topology-changes/628a0115-cd25-4f7c-8e2a-d29bc0cf44a9

Resume after approval by verifying `registry status` reports converged and ready, then begin Part 9's rejection, resubmission, supersession and recovery loop. Current disposable checkout remains clean at commit `287dee1`; the earlier user-authorized Notifications proposal is already applied.


## Parts 8–9 completed

The user authorized all proposals for the session. Approved telemetry rehome `628a0115-cd25-4f7c-8e2a-d29bc0cf44a9` in Chrome and verified converged/ready.

Part 9: config pin commit `432a48a` produced pending review `1ac2cfd7-94ff-44dc-b0dc-5de2ac919652`. Filtered review listing, JSON listing, URL recovery (`status: printed`) and immutable report retrieval all worked. Rejected with the tutorial note; the same unchanged commit produced new pending ID `0477ed20-cf1c-4ff6-b082-e32448e76941`. Billing retier commit `8734089` produced the two-action successor `bdab8f72-c4a8-4daa-a909-0840d58f9077`. The old Chrome review displayed “Proposal replaced,” disabled decisions, and a working “Open the current review” link. CLI JSON retained the successor ID and URL. Rejected the successor; commits `972519d` and `3233414` restored accepted state. Plan and sync found no changes; status reported converged, no current proposal, and ready provisioning. No manual recovery was needed. The optional two-source stale lab was not run.

Additional clarity observation after rehome: CLI organization correctly places private telemetry in Configuration, but its Dependencies list still shows `library.observability → library.config`, while the browser package graph draws telemetry's edge inside Configuration. Clarify the distinction between retained group references and current package dependency homes so these views do not appear contradictory. This is an observed presentation mismatch; no claim is made that package routing is broken.


## Part 10 preparation and credential approval checkpoint

Resolved both packages in Chrome:

| Package | Package group | Tier | Authoritative group ID |
| --- | --- | --- | --- |
| meridian-auth | library.auth | public | d912002c-157a-45cd-a98b-94ce0165fb06 |
| meridian-search | library.search | private | d59a7fdd-65b4-4cd0-b5fe-37aa0105ae70 |

Both panels supplied distinct server-issued staging/production index names, matching scoped personal-token links, secret-free named-profile CLI commands, and a separate device-connection installation path. The auth token form correctly prefilled exactly `package.upload`, `promotion.request`, and `ci.evidence.submit`, with `library.auth` selected. Prepared name “Meridian auth tutorial release” and seven-day expiry (September 12, 2026). No release token was created. The corresponding second token will be “Meridian search tutorial release,” with the same three operations and expiry, restricted to `library.search` staging.

**Execution authorization hold, not an Orbit failure:** automatic approval review rejected Create token because creating credentials with package-upload, promotion-request, and CI-evidence authority was not explicitly covered by permission to approve proposals. No alternate creation mechanism or bypass was used. The token table still contains only the existing `registry.manage` initialization credential. User authorization is needed for these two exact scoped release credentials, stored through CLI stdin/hidden login in the operating-system keychain. Chrome is left on the prepared auth token form; the create action has not been retried.

Built all four expected distributions outside the checkout at `/private/tmp/orbit-journey.KRpGqi/releases`. Both search distributions contain `Requires-Dist: meridian-auth`. Installed the two local wheels into a fresh Python 3.12 environment and successfully imported both packages; this is local preflight only, not CI evidence or a registry download. The checkout remains clean at `32334149f4911f3cd870ced1a2f1e398c56f59c7`.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| auth/meridian_auth-0.1.0-py3-none-any.whl | 1096 | cc80782033f3dc77617e22fae4c0cddedea0bd948b99855b697e6fab1fc55539 |
| auth/meridian_auth-0.1.0.tar.gz | 486 | 9df1eb8807a8fcc5b0423fde53c3d2052efaa4df2490ac6e4d3332e8a57aa9be |
| search/meridian_search-0.1.0-py3-none-any.whl | 1095 | 745179c4dc7d0770cf539b600d72ff236c514d67dc9aa8010868c46300bb74f8 |
| search/meridian_search-0.1.0.tar.gz | 522 | 9089e6275392b92c6f3cd3cbee7ea65989e39b9957418cfd0ce6f86c0c5c700e |

New findings:

- **Installation entry points select different credential flows.** The tenant home’s “Set up installation” and Quickstart links navigate to `settings/personal-access?operations=registry.read`, and Chrome confirms a tenant-wide personal-token creation dialog with `registry.read` selected. Connect and publish instead directs installers to account-level Package connections and `registry configure uv`, matching Part 12’s read-only device credential. Route both home actions to the device-connection setup, or explain when each credential type is appropriate. No token was created to test the legacy path.
- **The promotion copy command omits the next required step.** Connect and publish suggests `registry promote ... --wait`, but offers no CI-evidence submission example or explanation before that command. Part 11 explicitly says to capture the candidate without waiting, gather real CI, bind the manifest hash, submit evidence, and then approve. Surface those pending states and next actions beside the command; otherwise a first-time publisher may wait on a gate they have not learned to satisfy. No timeout was manufactured because uploads are still blocked by the execution authorization hold.
- **Positive separation:** the publishing screen clearly distinguishes staging uploads, immutable production promotion, and read-only installation credentials. Group scoping is correctly prefilled, and expiry is easily changed once the control is located.

Read-only checks of later prerequisites: Releases has no promotion history and explains that staging artifacts are required first. Account Package connections shows zero connections; `registry device status` reports credential absent, uv/pip configuration present, and a keyring helper from `/Library/Frameworks/Python.framework/Versions/3.12/bin/keyring` rather than the registry-installed copy. No user installer configuration was changed. GitHub account `GabrielCostanzo` has ADMIN access to `GabrielCostanzo/orbit-demo`, whose Build and import workflow is active (workflow ID 350834381). The audit clone still has only its local filesystem origin; no audit commit has been pushed, and there is no genuine CI run for this revision. Parts 11–13 require that later external-publication step; no Git pushes or release tags are authorized or performed by this checkpoint.

Resume after token authorization: create the two seven-day scoped release credentials, transfer each one-time secret directly to `registry login --key-stdin` without printing it or saving it in the report, verify each profile with `registry connect`, and publish the already-built wheel and sdist for auth then search. Continue through exact promotion candidates, genuine CI, consumer installation, and the Launchpad loop as prerequisites become available.


## Publishing completed; immutable candidates captured

The user explicitly approved both scoped tokens and then authorized creating or approving anything within the Orbit staging application. Both seven-day tokens were created, verified with `registry login`, and stored as `meridian-auth-release` and `meridian-search-release` in the OS keychain. Each has only `package.upload`, `promotion.request`, and `ci.evidence.submit`, bound to its respective package group's staging scope. `registry connect --tool twine` returned the expected authoritative targets. Both wheel/sdist pairs uploaded successfully, with a clean checkout.

Auth promotion `bfbcfde4-d2d8-4334-80aa-ab1e2eaded3b` binds manifest `f473ed3afcac6db85ab7b21303751e7a8c16afae03a5740046e591513e219691`. Search promotion `f236e6e7-018a-4c01-a6f2-a39e506d4bb7` binds manifest `6b434ef77b0cc5e6ec9ec47c836e6eb83ac73d04039aa6405a4e3eacefb426dd`. Both use `release-policy/v1` hash `3d01943896c19ecbe9680f3b12b0d8da760dc953efacedc4dd15f3a598290bcf`. Compared all four candidate filenames, sizes, and SHA-256 digests to local artifacts; all match. Both reviews were inspected in Chrome and are pending with no CI decision, approval, or production execution attempt. Providing a reason enabled Reject but correctly left Approve exact candidate disabled without CI. No CI evidence was fabricated.

New findings:

- **Scoped-token confirmation teaches a conflicting next step.** After creating the staging-only auth token, “Use it from CI” suggested `export REGISTRY_API_KEY=…`, a credential-bearing direct-index install URL, and a placeholder Twine upload. The preceding publishing page and tutorial instead teach named CLI profiles in the OS keychain and a separate read-only consumer connection. Tailor the one-time dialog to the selected operations, reuse the known package-group target, and offer the matching `registry login` command. Do not offer installation instructions for a token with no read operation. No secret is included in this report.
- **Token inventory omits the identifying scope.** Both release tokens show identical “staging · package group” scope labels. The selected group name or ID is absent from the list, forcing users to rely on names they typed themselves to distinguish authority. Show `library.auth` / `library.search` alongside staging.
- **Release review uses four columns inside a narrow content pane.** At the normal 1244×896 Chrome viewport, the navigation and Members sidebar leave approximately 600 px. Manifest, Policy, Source and Production remain four skinny cards; long identifiers wrap every few characters and stretch the row to roughly 400 px. The approval gate and evidence are below the first screen. Use a responsive two-column or stacked layout, collapsible/copyable hashes, and a prominent “Awaiting CI evidence” next action. Screenshot saved as `release-review-narrow.png` in the audit work directory.

Recovery notes, scoped to this automation environment: the first resumed Create click returned to the token list without saving a token or showing an error; a refreshed inventory confirmed only the init token before a successful retry. Copy token produced an empty clipboard in both the browser-session and OS clipboard checks, and CLI login refused the empty input. The visible one-time code was transferred directly through a private FIFO to `registry login --key-stdin`; both logins succeeded and the FIFOs were removed. A CUA child process without expanded network permission produced a transport error before the successful authorized CLI transfer. These observations do not establish that human clipboard use or the backend is broken. No duplicate release token was created, and no secret was printed or written to a regular file.


## Consumer setup and release preparation completed

Created account-level read-only device connection “Meridian tutorial audit 2026-09-05,” expiring October 5, 2026 (the shortest offered expiry was 30 days). Its credential is stored in the OS keychain. The one-time dialog exposes the credential as code but has no Copy button or installer command; users must manually select it and find setup instructions elsewhere. Add a copy action and the matching `registry configure` command.

The existing user uv configuration is not the exact configuration managed by this registry origin. Automatic approval review rejected a command targeting that file. A safer isolated test used the installed CLI's `configure_home` parameter under `/private/tmp/orbit-journey.KRpGqi`: an unmanaged blank-file fixture was correctly refused with exit 4 and preserved; a separate empty consumer directory was configured successfully, showing the expected secret-free diff. The user's actual uv/pip files were not modified. This exercised CLI configuration logic with a temporary destination, rather than completing the literal `--user` write to the user's home.

The isolated device-status check reported credential present, uv configuration present, gateway probe usable, and authenticated. The first consumer install waited in the default Python keyring helper. Stopped only that audit process group and retried with the helper installed alongside registry, which completed. The user then confirmed selecting Always Allow on the macOS keychain prompt; a retry with the normal helper also completed. Both authenticated `--no-cache` install attempts correctly reported no version of `meridian-search==0.1.0` while its promotion is still pending. No successful production download is claimed.

Additional tutorial findings:

- **Part 13's pinned Launchpad command fails.** `/Users/costanga98/.local/share/uv/tools/launchpad-uv/bin/launchpad --version` reports 0.1.1, and `launchpad init --baseline-tags --yes --ci none` returns `unknown flag: --ci` without changing the checkout. This version exposes `--workflow`, contradicting the page's note that it has no such flag. Retrying `init --baseline-tags --yes` worked and generated only towncrier/Launchpad metadata. Test the documented command against the pinned published binary. The Mac's default `launchpad` is a different Go snapshot, so also verify the executable and version after installation.
- **Sandbox clone guidance is outdated.** Part 0 says a clone inherits its source-keyed sandbox context. A second clone in this audit instead reported `registry_tenant_missing`; the installed context implementation intentionally keys disposable sandboxes by the resolved checkout path and rejects reuse of old source-keyed sandboxes. Update the explanation and distinguish persistent repository bindings from checkout-local sandboxes. Continued release verification in the original connected checkout.
- **Cleanup can invalidate the following part.** Part 12 places device logout and release-token revocation before the link to Part 13, which requires the auth release profile and consumer connection. Explicitly defer cleanup until after Part 13 for readers continuing the journey. No audit credential has been revoked yet.

Local Part 13 preparation was performed in a second disposable clone so 0.1.0 publication could stay ready. Commit `39b8cb6` adopted Launchpad metadata, `8b11f37` extended the auth package docstring and recorded the feature fragment, and `a4db80459e4e56d4d268fb6ce33d594933ff9f08` cut auth 0.2.0, consumed the fragment, updated changelogs and lockfile, and created an annotated `meridian-auth/v0.2.0` tag. Both auth 0.2.0 and search 0.1.0 built and imported in a fresh local environment. This is preparation and local preflight, not a completed production release loop.

Launchpad's `--no-push` still fetches/checks the current remote branch. The unpublished audit branch therefore could not be released against GitHub. A disposable local bare remote supplied that local preparation boundary; no remote GitHub ref was created. Auth changelog links were filled with the verified destination `GabrielCostanzo/orbit-demo`. Imported the finished branch and its two auth tags into the original connected checkout, where `registry status` confirmed `repository_ahead`, “converged (metadata-only ahead — nothing to do),” no current proposal, and ready provisioning.

## Concrete GitHub authorization handoff

The remaining production/installation checks need genuine GitHub Actions evidence. Both prepared revisions have zero provider runs. The user authorized all creation and approval actions within the Orbit staging application, while the session's AGENTS.md instructions separately say “Never push to a git remote unless asked.” No GitHub push has been attempted.

Proposed destination: `https://github.com/GabrielCostanzo/orbit-demo.git`, where the authenticated user has ADMIN access and the existing Build and import workflow is active. The following branch and tag names were absent in the read-only remote check. Publish these exact refs, without force or changes to GitHub main:

| Remote ref | Prepared value | Purpose |
| --- | --- | --- |
| `refs/heads/codex/orbit-journey-2026-09-05` | `32334149f4911f3cd870ced1a2f1e398c56f59c7` | Real CI for both staged 0.1.0 candidates |
| `refs/heads/codex/orbit-journey-release-2026-09-05` | `a4db80459e4e56d4d268fb6ce33d594933ff9f08` | Real CI for the prepared auth 0.2.0 release |
| `refs/tags/meridian-auth/v0.1.0` | Local annotated baseline tag at `3233414` | Auth baseline |
| `refs/tags/meridian-auth/v0.2.0` | Local annotated release tag at `a4db804` | Auth release anchor |

Prepared diffs are saved with this report in `journey-review-2026-09-05/catalogue-accepted.patch` and `journey-review-2026-09-05/launchpad-release.patch`. Neither contains credentials or audit runtime configuration. Other locally generated baseline tags stay in the separate preparation clone.

After authorization: push those exact refs, wait for the real Build and import runs, bind each 0.1.0 candidate manifest to the run for `3233414`, approve/promote auth then search in Chrome, prove the real consumer download, then run `registry release` from `a4db804` with the real release-commit CI result. Inspect and approve the resulting auth 0.2.0 promotion, install it through the consumer gateway, and finish deliberate credential cleanup. The original user uv/pip configuration must remain outside this audit; use the generated temporary config explicitly.

Current local paths: connected checkout `/private/tmp/orbit-journey.KRpGqi/meridian`; profiles/context under `/private/tmp/orbit-journey.KRpGqi/registry-config`; consumer config `/private/tmp/orbit-journey.KRpGqi/consumer-home/.config/uv/uv.toml`; consumer venv `/private/tmp/orbit-journey.KRpGqi/consumer/.venv`; candidate documents `/private/tmp/orbit-journey.KRpGqi/releases/{auth,search}-promotion.json`. The second preparation clone and local bare remote are also preserved under the same audit directory.

![Release review at the normal Chrome viewport](/Users/costanga98/workspace/dev/orbit-demo/tutorial/journey-review-2026-09-05/release-review-narrow.png)


## Real CI, production promotion, and consumer installation completed

After explicit authorization, an atomic push published exactly the two proposed audit branches and the annotated auth 0.1.0/0.2.0 tags to `GabrielCostanzo/orbit-demo`. Both Build and import workflows passed: [0.1.0 audit run 33994200391](https://github.com/GabrielCostanzo/orbit-demo/actions/runs/33994200391) at `32334149f4911f3cd870ced1a2f1e398c56f59c7`, and [0.2.0 release run 33994200182](https://github.com/GabrielCostanzo/orbit-demo/actions/runs/33994200182) at `a4db80459e4e56d4d268fb6ce33d594933ff9f08`. Provider job/step results confirmed both builds and the cross-package import check. Chrome's separate GitHub session returned a logged-out 404 for the private run page; authenticated `gh` verified the actual provider results. This is a browser-session limitation, not failed CI.

Submitted genuine run 33994200391 evidence bound to each exact 0.1.0 manifest. Inspected source/production indexes, both artifact digests, policy, run and revision in Chrome. Approved auth before search; both UI and `registry promote --wait` reported `succeeded`, with one successful execution attempt each. A `--no-cache` install into the previously empty consumer venv requested only `meridian-search==0.1.0`, downloaded both search and auth 0.1.0 through the single configured gateway, and printed `meridian-search resolved meridian-auth`. No source-ambiguity recovery was needed.

`registry release --workspace . --ci-result … --profile meridian-auth-release --json` then completed its build, upload, candidate capture and CI submission from the clean tagged release commit. It returned exit 0 with pending promotion `58fb356a-fcfc-48fd-87fb-e91cd96267df`, preserving the human gate. Chrome showed manifest `bed257362276a1fc6350312041406225aec97fbd51bd876a401e889ae4dd91da`, the same release policy and authoritative auth indexes, and passed run 33994200182 at the exact release commit. Both artifacts matched the independent preflight build:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| meridian_auth-0.2.0-py3-none-any.whl | 1174 | ad30b1373a8231f47c3730d1bc7863520d011490487e82e7ab75d2fb9445c080 |
| meridian_auth-0.2.0.tar.gz | 1047 | 1a7e7321f222764a58a3090e1204616c9a29640f5067bf4f489c32dce537d78b |

Approved in Chrome and observed `succeeded`, approved decision/reason, and `Attempt 1 · succeeded`. Installing auth 0.2.0 with cache disabled replaced 0.1.0; metadata reported search 0.1.0 plus auth 0.2.0, both imported, and the installed auth module contained the changed docstring. This completes the actual release-to-consumer loop.

New findings:

- **The release summary cannot support its prescribed verification.** Part 13 Step 8 asks readers to compare the candidate manifest hash against `release-summary.json`, but the successful JSON contains only release commit, package/version/tag, artifact filenames, promotion ID/state, and exit code. There are no artifact sizes/digests, manifest hash, policy hash, or review URL. Include the captured candidate identity and review URL, or document a supported command that retrieves them. This audit recovered by comparing the browser's artifact digests to the independent local tagged build.
- **The final install command assumes a project that was never created.** Part 13 Step 8 says to run `uv add "meridian-auth==0.2.0"` from the Part 12 consumer project. Part 12 only creates a venv. Running the prescribed command in that directory fails with exit 2: `No pyproject.toml found in current directory or any parent directory`. Reusing Part 12's `uv pip install` pattern succeeds. Either keep that pattern or add explicit project initialization before `uv add`.
- **CI evidence is hard to verify from the review.** On all three releases, the UI renders provider, run ID, and full revision as plain text, with no link to the supplied `details_url`. Add an “Open CI run” link and a copyable commit identifier so a reviewer can inspect the primary evidence directly.

Positive verification: staging-only installation failed as expected before promotion; after real evidence and browser approval, the exact versions became downloadable. All three promotions succeeded in one execution attempt. The release helper preserved the same approval gate as the manual workflow.


## Cleanup and final verification

`registry device logout` removed the audit consumer credential and explicitly reported the isolated uv configuration left behind. Removed only `/private/tmp/orbit-journey.KRpGqi/consumer-home/.config/uv/uv.toml`. The isolated status check then returned the expected not-configured exit 2: credential absent, uv/pip config absent, probe skipped. The actual user uv/pip configuration was never changed. Chrome confirmed “Meridian tutorial audit 2026-09-05” is Revoked.

The user explicitly authorized revocation of **Meridian auth tutorial release** (profile `meridian-auth-release`, auth-group staging) and **Meridian search tutorial release** (profile `meridian-search-release`, search-group staging). Revoked both through Chrome and verified each row shows **REVOKED**, with the inventory reporting **Active (1)** and **Inactive (2)**. The separate initialization management credential remains active. The earlier automatic-approval hold is resolved; no alternative revocation mechanism was used.

Removed the two revoked credentials from the OS keychain using the installed credential-store deletion routine after matching each profile's origin, tenant, public prefix and operations. Verified both keychain entries are absent, then removed only their isolated profile metadata files. No audit consumer or release credential remains usable. The immutable production releases, promotion history, live Product and sandbox are preserved as audit evidence.

Local cleanup guidance is slightly outdated: Part 12 says release-profile files contain revoked secrets and may be removed. The installed `ProfileStore` writes secret-free metadata and stores the actual key in the OS keychain; `registry logout --help` confirms there is no profile logout command. Removing the JSON alone would leave the keychain entry. This audit completed both steps through the installed store routine; users need a documented or public CLI equivalent.

A final layout observation: at the normal Chrome viewport, the token table needs horizontal scrolling. Reaching the status and action columns moves the token names out of view. A sticky name column or stacked token rows would preserve identity while reviewing authority and revocation status; the confirmation dialog does correctly repeat the token name.

The main tutorial journey and deliberate credential cleanup are complete. No manual action remains pending. Owner-only and isolated-installer scope limits remain as listed above.

Final `registry status` verifies the staging connection, metadata-only repository-ahead convergence, no current proposal, ready provisioning, and “No command required.” The connected disposable release checkout is clean. The two approved GitHub audit branches and auth tags remain; GitHub main was not changed. All audit reports/evidence are local commits only and have not been pushed.


![All three promotions succeeded in Chrome](/Users/costanga98/workspace/dev/orbit-demo/tutorial/journey-review-2026-09-05/releases-complete.png)


![Both audit release tokens revoked in Chrome](/Users/costanga98/workspace/dev/orbit-demo/tutorial/journey-review-2026-09-05/release-tokens-revoked.png)
