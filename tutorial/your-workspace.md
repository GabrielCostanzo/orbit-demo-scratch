# 7. Use your own workspace

Apply the same workflow to one of your team's Python libraries or Applications.

## Connect a real repository

Start in your own clean uv workspace. Add a root configuration, changing the
source key and slug to identify your repository:

```toml
[tool.orbit.registry]
schema = 2
source_key = "your-team/your-repo"
workspace_slug = "your-team"
default_tier = "private"
fallback_resource = "library.shared"
placement_policy = "follow"
upstream = "pypi"
```

Commit the configuration, then inspect what Orbit infers:

```bash
registry topology validate --workspace . --json
registry init --origin https://orbit-staging.home.costanga.com
```

Review the package homes, access tiers, and dependencies before approving.
Without `--sandbox`, this creates a persistent binding. Commit the generated
`.orbit/registry.json` so teammates connect to the same registry.

## Repeat the useful parts

| Your next task | Use |
|---|---|
| Share a starter library | Mark it `public`, commit, plan, sync, and approve |
| Offer an add-on | Promote its Project to a Product and configure access |
| Introduce the registry | Fill **Registry storefront** so the home, the invite page, and the Discover card describe it |
| Bring in teammates or customers | Share an invite link from **Members & roles**, or set **Registry settings → Discoverability** and approve join requests |
| Publish from CI | Create a staging key per package group; build, upload, submit real CI evidence, approve |
| Publish an Application image | Open its **Images** page, set up storage, and use **Connect CI** |
| Vary checks by source | Create named **Validation profiles** and ordered rules for the approved publishing connection |
| Run checks automatically | Configure **Validation hooks** and an authenticated result reporter in your CI system |
| Inspect a potential deployment | Open build **Details → Current policy**; use the target profile's **Deployment guard** in CI |
| Apply changed requirements to an existing image | **Reassess under current policy**; keep the digest and inspect the new assessment |
| Install on a workstation | Create a Package connection and configure uv once |
| Reconcile a repository change | `registry topology plan`, `registry topology sync`, then review |
| Find the next action | `registry status` |

Choose your actual Orbit origin for continued use. The billing helper is
specific to this demo; use the [publishing guide](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/guides/publish.md)
and [workspace reference](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/reference/workspace-config.md)
for your own automation and layout.

## Explore more when needed

The [optional topology labs](catalogue/README.md) cover shared libraries,
Applications, identity-preserving renames, sensitive reviews, and recovery.
Start those in a fresh demo sandbox so they
can safely exercise topology changes before any artifacts are published.

**Result:** your first real repository is connected, with a workflow you have
already used from creation to customer installation and Application validation.
