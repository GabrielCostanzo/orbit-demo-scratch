# 6. Publish an Application image

Turn Meridian's existing `billing-api` Application into a runnable image. A push
adds the image to Orbit; its CI source selects a validation profile; the requested
checks run outside Orbit and report against that exact image digest.

| Part | You will see |
|---|---|
| This page | Ready image storage for the existing Application |
| [Connect publishing](images/publishing.md) | One CI integration, using the same tested wheels as the package journey |
| [Configure validation](images/validation.md) | Preview and Release profiles, automatic requests, and real results |
| [Inspect decisions](images/decisions.md) | The build pool, policy changes, reassessment, and a deployment guard |

The billing image contains the five wheels from **Build and test distributions**.
It serves `/health` and `/invoices`; the sample invoices still total **$48.00**.
Its Dockerfile installs those wheels directly. It does not resolve newer versions
from an index or rebuild workspace members. Package promotion to customers stays
independent of this Application's validation.

## Prepare the runner — owner

Continue in the same fork and sandbox as the previous chapters. Run
`./demo setup` again if your CLI predates Application images. Have:

- Your owner browser session, or the image, CI-connection, validation-policy,
  hook-management, and validation-request permissions needed for these steps.
- A trusted Docker runner with Bash, `curl`, `jq`, Python 3, and Git. It must
  reach both Orbit and the image registry URL returned by storage setup.
- A place to run the validation receiver with the registry CLI and Docker, plus
  an operator-approved HTTPS endpoint Orbit can call. The publisher and validator
  may use the same dedicated runner; they have different credentials.

With the home-server staging instance, use a LAN or tailnet runner. Its validation
endpoint can also stay private when the operator has explicitly allowed that
destination. This chapter does not require public production ingress. Do not
enable untrusted fork jobs on a runner that can reach your services.

If the validation endpoint is not ready, you can configure storage and publishing
and inspect images. Requested validations will await results; that is an
incomplete walkthrough, not a passing validation.

## Open the Application

As the owner, open **Billing**, then **Applications → billing-api → Images**.
Use the developer/private view if you are looking at the customer storefront.
The Application is already declared in the accepted Meridian workspace; you do
not create another one for the image.

Choose **Set up image storage** and wait for **Ready**. Expand **Storage and push
setup** and inspect the push reference, quota, and discovery status. Orbit
provisions the backing registry. You use the returned reference and Orbit's CI
configuration without creating a Harbor account or project.

Record the tenant and Application UUIDs from this page's URL:

```text
/+app/t/<tenant UUID>/applications/<Application UUID>/images
```

Use your actual UUIDs wherever the later pages say `REGISTRY_TENANT` and
`ORBIT_APPLICATION_ID`. To inspect the same binding in the CLI, set those values
in your shell, then run as the owner:

```bash
export REGISTRY_URL=https://orbit-staging.home.costanga.com
# Set REGISTRY_TENANT and ORBIT_APPLICATION_ID from your own Images URL.
registry images status --tenant "$REGISTRY_TENANT" \
  --application "$ORBIT_APPLICATION_ID" --device
```

**Result:** one ready image-storage binding on Meridian's billing Application.

**Next: [Connect publishing](images/publishing.md).**
