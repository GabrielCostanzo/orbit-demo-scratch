# Demo commands and recovery

Run `./demo --help` from the checkout. The launcher requires uv; it runs a
standard-library Python helper without installing the workspace into itself.

| Command | What it does |
|---|---|
| `./demo setup [--source /path/to/orbit]` | Install the tested CLI from source, keyring helper, and Launchpad 0.1.1 |
| `./demo status` | Show the checkout connection, registry status, and last completed release |
| `./demo login billing` / `auth` | Resolve the checkout's tenant and save a scoped key through a hidden prompt |
| `./demo build [--out /empty/path]` | Build five wheel/sdist pairs; install and test the wheels outside the workspace |
| `./demo image-context --artifacts /path/to/distributions` | Verify artifact identity and hashes, then copy the exact five wheels into the ignored Docker context; no package rebuild |
| `./demo validation-tools --out /empty/path [--source /path/to/orbit]` | Copy Orbit's existing receiver/reporting adapter and Meridian's real image checks; starts no service |
| `./demo publish sdk` / `bundle` | Find real CI for HEAD, verify and upload its artifacts, submit evidence, wait for human approval |
| `./demo install sdk` / `billing` | Download the current workspace version into a fresh temporary venv and run invoices |
| `./demo launchpad …` | Run the pinned tool even if another `launchpad` is on PATH |

`publish --run RUN_ID` selects a specific successful push or manually dispatched
run. CI artifacts expire after seven days. The helper never approves a release,
pushes Git, or creates CI evidence from a local test. It verifies repository,
commit, run attempt, filenames, sizes, and digests before binding evidence to
Orbit's candidate.

Non-secret progress lives under `~/.local/state/orbit-demo/` (or
`$XDG_STATE_HOME/orbit-demo/`), keyed by checkout. Credentials remain in the
registry CLI's OS keyring. Temporary consumer environments are removed on exit.
Image publisher keys, validation-reporting keys, and deployment-read keys belong
in the runner's secret store. `setup` also records the non-secret Orbit source
path so `validation-tools` uses the same source installation.

## Resume a chapter

| Where you stopped | Continue with |
|---|---|
| Sign-in, creation, or provisioning | `registry init` |
| Release approval | Rerun the same `./demo publish … --run RUN_ID`; open its printed review |
| Ordinary topology review | `registry status`, then its suggested command |
| Customer acquisition | Reopen Billing as that customer; complete the outstanding requirement |
| Consumer install | Correct the connection/access issue below, then repeat `./demo install …` |
| Membership (invite link, join request) | Owner: **Members & roles → Invite links** or **Join requests**; customer: reopen the link or the Discover preview |
| Image publishing | **Billing → Applications → billing-api → Images → CI connections**; inspect the publishing job and storage status |
| Automatic checks | Open the assessment's validation rows and delivery details; see [Validation](images/validation.md) |
| Changed deployment requirements | Read **Details → Current policy**, then use **Profile assessments → Reassess under current policy**; see [Decisions](images/decisions.md) |

## Installer configuration

`registry configure uv --user` makes Orbit the user's default package index.
If it reports an unmanaged file, preserve that file before retrying, for example:

```bash
mv -n ~/.config/uv/uv.toml ~/.config/uv/uv.toml.pre-orbit
registry configure uv --origin https://orbit-staging.home.costanga.com --user
```

If the backup already exists, choose another name; do not overwrite it. After
the demo, device logout prints the managed file to remove. Restore your backup
to its original location. Follow the actual path printed by the CLI if your
configuration directory differs.

## Install failures

| Symptom | Next action |
|---|---|
| First macOS download waits | Answer the visible Python keychain prompt; allow future access if desired |
| Authentication fails | Run `registry device status --origin https://orbit-staging.home.costanga.com`; replace an expired/revoked connection |
| No matching package/version | Check production promotion succeeded and this account has the required access |
| Gateway `409` after several demos | In Package connections, choose this sandbox as the package source, including its dependencies |
| Access looks unlocked as the customer before requesting | Verify this is an ordinary member account with no staff role |
| Release reports a different tenant or scope | Recreate the intended scoped key and rerun `./demo login billing` or `auth` |
| Install fails right after rejoining a registry | Leaving removed Product access; request the Billing engine again or add a manual grant. The SDK still installs |
| **This invite is no longer valid.** | Create a fresh link under **Invite links**; the old one expired or was revoked |

## Image recovery

| Symptom | Next action |
|---|---|
| Docker build cannot find `.orbit-image-context` | Download this run's `meridian-distributions`, then run `./demo image-context --artifacts …` before the generated publish steps |
| Image context already exists | On the disposable runner, remove only the generated `.orbit-image-context` and prepare it again; the helper never overwrites it |
| CI artifact attempt differs | Rerun **all jobs** so package inputs and image publishing share the same run attempt |
| Image has no source or is Unclassified | Inspect the publishing job's source-report step, event/ref, selected connection, and saved source rules; a Docker tag alone does not select a profile |
| Checks await results | Inspect the hook destination and delivery; accepting a request does not mean its check passed |
| Check reports an unsupported definition | Match the workflow/version/parameters in [Validation](images/validation.md), or update the external check implementation with the definition |
| Requirements met but deployment denied | Read **Current policy**; saved requirements can differ from current ones. Reassess the concrete source after reviewing the reason |

For lower-level steps, use Orbit's [publishing](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/guides/publish.md)
and [device connection](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/guides/connect-device.md) guides.

## Verify the runnable image without an Orbit connection

On a Docker runner, run `python3 tests/verify_image_runtime.py`. It builds and
tests the five distributions, prepares their exact wheels, builds and pushes the
image to a disposable registry bound to loopback, and runs smoke and regression
against its real digest. It removes its own image and containers afterward.
This verifies the demo runtime; it does not prove CI identity, Orbit discovery,
hook delivery, or deployment eligibility. Those require the real
[Application journey](images.md).
