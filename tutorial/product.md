# 3. Offer the billing engine

Northstar needs automatic ledger entries as well as an invoice preview.

## Publish the bundle — owner

In **Connect and publish**, resolve `meridian-auth`. Create another 7-day
release token using its preselected `library.auth` staging scope, then:

```bash
./demo login auth
./demo publish bundle
```

Approve each printed review. The helper releases auth, models, ledger, and core
in dependency order; Billing reuses its existing release key.

## Configure the Product — owner

1. Under **Projects**, hover **Billing → Promote to product** and confirm.
2. In **Storefront details → Edit**, use summary `Preview invoices. Automate billing.`
   and description `Turn invoice batches into balanced ledger entries.` Save.
3. In **Contents and access → Edit**, choose **Choose resources and requirements**.
4. In **What customers can use**, select only `meridian-billing-core`.
   Ledger and models are bundled automatically; auth and the SDK are public
   dependencies. Continue.
5. In **Details**, name the option `Billing engine`; describe it as
   `Process invoices into ledger entries.` Continue.
6. In **Requirements**, add **License acceptance**. Under **Create a license…**,
   choose **Evaluation (non-production)**. Fill its placeholders with `2026`,
   `Meridian Demo`, and `30 days`. Create the revision and add the requirement.
   Also add **Administrator approval**, with instructions `Request a demo evaluation.`
7. Review and **Save access**, then **Activate storefront → Activate → Done**.

**Checkpoint:** **View live** shows the included SDK and the Billing engine
add-on. The separate operator CLI stays hidden because this option does not
include it. Your owner account shows **Staff access**.

## Introduce the registry — owner

Open the registry's title menu and select **Registry storefront**. In
**Storefront details → Edit**, use summary `Billing toolkit for Meridian partners.`
and description `Invoice previews for every member; the billing engine by
evaluation.` Save, then select **View live**.

**Checkpoint:** the registry home shows the summary under its name,
**Included with membership** lists `meridian-billing-sdk` and `meridian-auth`,
and **Products** shows Billing. Invited people see this summary before they join.

## Invite the customer — owner

Open the title menu and select **Members & roles**. Under **Invite links**, keep
**Expires in** at **7 days**, select **Create invite link**, then **Copy link**.
The full URL is shown only now; the row keeps its prefix, **Active**, and
**0 joined**. Orbit sends no invitation email, so paste the link where the
customer can open it.

## Join as a customer

Use a separate browser profile or private window so the owner session stays open.
Open the copied link and register a second account, such as `northstar-demo`.
The **Invited to join** page shows the registry name, summary, member count, and
the link's expiry. Select **Join registry**.

**Checkpoint:** the registry home opens with its tile in the rail. As the
**owner**, refresh **Members & roles**: the customer is listed under
**Current members** with no roles, and the link shows **1 joined**. Membership
alone unlocks only public packages such as the SDK.

As the **customer**, open **Billing → Billing engine → Request access**.
Review and accept the exact license revision. The request remains pending.

As the **owner**, open **Administration → Access requests**, select this
customer's request, enter a reason, and **Approve**.

**Checkpoint:** the customer refreshes Billing and sees the engine, ledger,
and models unlocked.

## Install as the customer

Switch the workstation's package credential to this customer:

```bash
registry device logout --origin https://orbit-staging.home.costanga.com
```

In the **customer's** account menu, create a **Package connection** named
`Northstar evaluation`. Paste that credential into:

```bash
registry configure uv --origin https://orbit-staging.home.costanga.com --user
./demo install billing
```

Expected output:

```text
3 invoices · total $48.00
6 ledger entries · debit $48.00 = credit $48.00
```

**Result:** one install includes the protected dependency chain and shared
public dependencies. Product access changed in the browser; Git topology
did not change.

**Next: [Ship an update](release.md).**
