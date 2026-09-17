# 2. Publish and install the SDK

Share the invoice preview with everyone in your registry.

## Connect a publisher

As the **owner**, open **Connect and publish** and resolve
`meridian-billing-sdk`. Its home is `project.billing`, tier `public`.

Follow **Create or review personal access tokens**. Keep the preselected Billing
package group and staging operations (`package.upload`, `promotion.request`,
`ci.evidence.submit`); name the key `Meridian billing release`, with a 7-day expiry.
Create it, then paste the one-time secret into this hidden prompt:

```bash
./demo login billing
```

The management connection from step 1 remains available for topology work.

## Release the tested artifacts

Once **Build and test distributions** passes in your fork:

```bash
./demo publish sdk
```

The helper finds CI for the current commit, downloads its tested wheel and
source distribution, uploads them to staging, and submits the matching CI
evidence. No run IDs or hashes need to be copied.

Open the review URL it prints. Check the package/version, source and production
targets, artifacts, and linked CI run. Enter a decision reason and select
**Approve exact candidate**. The terminal waits for production to be ready.

**Checkpoint:** `meridian-billing-sdk 0.1.0: production ready.`

## Connect an installer

In the account menu, open **Package connections → New connection**. Name it
`Meridian owner`, choose an expiry, and copy the one-time `dpc_…` credential.

```bash
registry configure uv --origin https://orbit-staging.home.costanga.com --user
registry device status --origin https://orbit-staging.home.costanga.com
```

Paste the credential only into the hidden prompt. Review the configuration
change; it sets Orbit as uv's default index and keeps the secret in your keychain.
On macOS, approve the Python keychain prompt when it appears.

If you already have an unmanaged uv configuration, the CLI refuses to overwrite
it. Follow [configuration recovery](tools.md#installer-configuration) before continuing.

## Run the installed SDK

```bash
./demo install sdk
```

This downloads into a fresh environment outside the repository and runs
`meridian-invoices examples/invoices.json`:

```text
3 invoices · total $48.00
```

**Result:** a real production package, installed through Orbit's single consumer
URL. The helper prints the underlying uv command so you can reuse it elsewhere.

**Next: [Offer the protected billing engine](product.md).**
