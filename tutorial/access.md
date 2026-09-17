# 5. Manage access and membership

End Northstar's evaluation, verify what changes for the customer, then open the
registry to Discover and watch the customer leave and rejoin.

## Revoke the evaluation — owner

Open **Billing → Storefront actions → Requests & grants**. Under **Manual grants**,
select the customer and inspect the Billing engine grant's acquisition source.
Select **Revoke** on that grant.

As the **customer**, refresh Billing: protected packages should be locked.
The workstation still holds the customer's package credential:

```bash
./demo install billing
./demo install sdk
```

The first command should fail to resolve the protected core. The second still
prints the invoice total. Each command uses a fresh environment with cache
bypassed; revocation cannot remove code already downloaded.

## Try an explicit grant — owner

On the same page, select the customer and the active Billing engine benefit,
enter reason `Support extension`, and select **Grant**. Run
`./demo install billing` again to verify access, then revoke this grant.
The history distinguishes the manual extension from the earlier acquisition.

For internal teammates, use **Members and roles** to assign only the roles they
need. Customer package access comes from Product benefits; assigning a staff
role would bypass the customer experience you just tested.

## Open the registry to Discover — owner

Open the title menu and select **Registry settings**. Under **Discoverability**,
choose **Discoverable** and enter the join terms
`Evaluation use only. No production deployments.` Select **Save** and wait for
**Saved**.

Select **Discover** in the rail, below **Create registry**. Your registry's card
shows the storefront summary, its member count, and **Request to join**.
Registries start **Hidden**, which is why the customer needed an invite link;
**Open** would let anyone signed in join without approval.

## Leave and rejoin — customer

As the **customer**, open the registry's title menu and select **Leave registry**,
then confirm with **Leave**. The tile disappears and the app lands on
**No registries yet**. Reopen the registry's address from your browser history:
because the registry is now listed, Orbit sends you to its Discover preview
instead of the home.

Read **Join terms** and select **I accept these terms**, then **Request to join**.
Enter the note `Northstar would like to keep evaluating.` and select
**Send request**. The preview shows **Request pending**.

As the **owner**, open **Administration → Members & roles**. Under
**Join requests**, read the note and select **Approve**. **Show decided** keeps
the decision and who made it.

As the **customer**, select **Back to Discover**: the card now says **Joined**.
Open it and select **Open registry**.

```bash
./demo install sdk
```

The SDK installs again through the same package connection, because membership
restored public access. Leaving removed the account's roles and Product access,
and rejoining did not bring them back: the billing engine would need a new
acquisition or manual grant.

## Clean up the package credentials

As the owner, open **Members & roles → Invite links** and select **Revoke** on
the active link; anyone opening it now sees **This invite is no longer valid.**
Existing members stay. Then revoke the two demo package connections in each
account's **Package connections**, and revoke the Billing and auth release
tokens in **Personal access tokens**.
Remove their local credentials:

```bash
registry device logout --origin https://orbit-staging.home.costanga.com
registry logout --profile meridian-billing-release
registry logout --profile meridian-auth-release
```

Device logout prints the managed uv configuration path. Remove that file as
instructed, then restore any configuration you backed up. Otherwise uv will
keep targeting Orbit without a credential. Local logout alone does not revoke
a server-side credential.

Keep the registry for the Application image chapter. Set **Discoverability**
back to **Hidden** so it leaves the shared Discover list, and keep your owner
browser session. Image publishing and validation use separate connections;
they do not reuse the package credentials you just revoked.

**Result:** you have exercised acquisition, revocation, manual access, discovery
with join terms, leaving and rejoining, and credential cleanup.

**Next: [Publish an Application image](images.md).**
