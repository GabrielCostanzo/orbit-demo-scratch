# 4. Ship an update

Northstar wants to preview only its own invoices.

## Record the change

Initialize the pinned release tool once:

```bash
./demo launchpad init --baseline-tags --yes --workflow solo
git add --all
git commit -m "release: adopt changesets"
```

In [the SDK command](../project/billing/package/meridian-billing-sdk/src/meridian_billing_sdk/__main__.py),
add this line immediately before `args = parser.parse_args()`:

```python
parser.add_argument("--customer")
```

Immediately after `invoices = read_invoices(args.invoices)`, add:

```python
if args.customer:
    invoices = [row for row in invoices if row["customer"] == args.customer]
```

Keep the surrounding indentation. Then:

```bash
./demo build
./demo launchpad fragment feature --member meridian-billing-sdk -m "Filter invoices by customer"
git add --all
git commit -m "billing: filter invoices by customer"
./demo launchpad release --no-push --member meridian-billing-sdk --no-dependents
git push --follow-tags origin main
```

Launchpad records the changelog and tags SDK `0.2.0`. CI tests the new behavior
when the filter is present. `registry status` can report metadata-only
`repository_ahead`; no topology proposal is needed for this code/version change.

## Publish and try it

Wait for your fork's CI run to pass, then:

```bash
./demo publish sdk
```

As the **owner**, follow the printed review and approve the exact `0.2.0`
candidate. The workstation still uses the **customer's** install credential:

```bash
./demo install sdk --customer Northstar
```

```text
2 invoices · total $28.00
```

**Result:** the customer gets an improved version through the same connection;
`0.1.0` remains immutable.

The helper publishes the exact CI-built artifacts. For your own release
pipeline, Orbit also supports [Launchpad's registry release integration](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/guides/launchpad.md).
Launchpad's terminal UI can also connect a workspace and inspect Orbit releases
through the optional [Orbit companion](https://github.com/GabrielCostanzo/orbit/blob/main/project/python-package-registry/docs/external/guides/launchpad-companion.md):
press `D` on a member and enable Orbit.

**Next: [Manage access and membership](access.md).**
