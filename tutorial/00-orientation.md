# 1. Create your registry

Start a disposable registry for Meridian's billing toolkit.

## Get the demo

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and
[GitHub CLI](https://cli.github.com/), then:

```bash
gh auth login
gh repo fork GabrielCostanzo/orbit-demo --clone
cd orbit-demo
./demo setup
```

`setup` installs the tested Orbit CLI and Launchpad. If you already have the
Orbit source, use `./demo setup --source /path/to/orbit` instead. The CLI is
currently distributed from source; it is not on PyPI. `setup` warns when the
pinned CLI revision differs from the revision the Orbit instance reports.

Open your fork's **Actions** tab and enable workflows. Select
**Build and test distributions → Run workflow** on `main` for the first run.
Future pushes run it automatically. The release helper uses this real CI result;
a local build cannot replace it.

Docker is needed only for the later [Application image chapter](images.md).
For the staging instance, run image publishing and validation on a runner with
LAN or tailnet access to Orbit and its image registry. The package-build job can
remain on GitHub's hosted runner. On the home-server setup, Docker workloads run
on the server; leave Docker Desktop stopped on the Mac.

## Connect

From the clean checkout:

```bash
registry init --origin https://orbit-staging.home.costanga.com --sandbox
```

1. Enter the terminal's one-time code in the page it opens. Sign in or select
   **Register** to create your owner account.
2. In the registry review, check your account, the `meridian-sandbox-…` name,
   and the source commit. Select **Approve and create registry**.
3. Return to the terminal and wait for **ready**.

Orbit derives package groups, packages, and Applications from the committed
workspace. The browser handles the review; the CLI keeps the connection in
your OS keychain.

```bash
./demo status
```

**Result:** a ready registry, converged topology, and no pending proposal.

If interrupted, run `registry init` to resume. Use
`registry init --sandbox --restart` only when deliberately starting over.

**Next: [Publish and install the SDK](publish.md).**
