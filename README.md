# Learn Orbit with Meridian

Meridian shares a billing SDK, gives a customer access to its billing engine,
and ships an update. Then you package the billing API as an image, request its
checks automatically, and verify whether it satisfies your deployment policy.

**Start here: [Create your registry](tutorial/00-orientation.md).**
You need Git, uv, a GitHub account for real CI, and a reachable Orbit instance.
The tutorial uses [Orbit staging](https://orbit-staging.home.costanga.com/+app).

| Step | Result | Orbit feature |
|---|---|---|
| [1. Start](tutorial/00-orientation.md) | Your own disposable registry | Workspace inference and reviewed creation |
| [2. Publish and install](tutorial/publish.md) | `3 invoices · total $48.00` | Scoped publishing, CI, approval, device connection |
| [3. Offer the billing engine](tutorial/product.md) | An invited customer installs the protected bundle | Registry storefront, invite links, Products, licenses, access requests |
| [4. Ship an update](tutorial/release.md) | Northstar's two invoices total $28 | Changesets, versions, immutable releases |
| [5. Manage access and membership](tutorial/access.md) | Grant, revoke, and let people find the registry | Grant provenance, discoverability, join terms, join requests, leaving |
| [6. Publish an Application image](tutorial/images.md) | A pushed image with source, validation results, and a current deployment decision | Image discovery, Connect CI, hooks, profiles, reassessment, deployment guard |
| [7. Use your workspace](tutorial/your-workspace.md) | A registry for your own packages and Applications | Persistent setup and everyday workflow |

Each page ends with a result and the next step. Continue in the same checkout;
`./demo status` shows its connection, pending review, and last completed release.
The image chapter also needs a Docker runner and a validation endpoint reachable
from Orbit. GitHub Actions is the tutorial's publishing path; Orbit also accepts
other CI systems through an Application-bound publisher key and signed webhooks.

## Optional labs

After the main path, explore [topology changes](tutorial/catalogue/README.md)
in a **fresh sandbox**: add a shared library, change tiers, inspect dependency
relationships, rename Applications, review sensitive changes, and recover proposals.

The [helper reference](tutorial/tools.md) explains the commands and common
recovery steps. To preview the invoice code locally, run `./demo build`; this
builds and tests real wheels without connecting to Orbit.

## Map it to your team

| Meridian | Your equivalent |
|---|---|
| Billing SDK (`public`) | A starter library available to every registry member |
| Billing engine (`protected`) | An add-on unlocked by a Product access policy |
| Shared auth library | A dependency reused across projects |
| Private telemetry and the billing API | Internal packages and a container Application |
| Invite link or Discover listing | How teammates and customers get into your registry |

“Public” means active registry members. The demo exercises access policy and a
small runnable billing API; it does not process payments. Your runner executes
the image checks. Orbit stores images, source associations, results, and policy
decisions; your CI/CD system owns deployment.
