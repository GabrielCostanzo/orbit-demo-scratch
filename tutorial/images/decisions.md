# Inspect the build and its current decision

## Read the pool — image reader

In **Billing → Applications → billing-api → Images**, inspect the Release and
Preview builds. Use the pool's filters and expand **Details**. Expect:

- A concise validation summary in the build row, with individual checks and
  their attempt history in the expanded details.
- **Bound image**: digest, tag, platforms, image reference, and the publishing
  source/run. Copy uses the full digest even when the display shortens it.
- A profile assessment with its concrete source association, saved policy
  revision, required/excluded entries, and results bound to that image.
- **Current policy**: a separate decision for each current profile, including
  why a build is allowed, denied, or not assessed for that profile.

Preview passing smoke does not qualify the feature build for Release. Its source
selected Preview, and Release requires more validation. There is no deployment
environment or running-host status here: Orbit has recorded an image and its
evidence, not deployed it.

## Try a guard without deploying — owner

Open **Validation profiles → Deployment guard** for **Preview**, and copy the
**Generic script** to `orbit-image-guard.sh` **outside this repository**. It fixes
the Orbit URL, tenant, Application, profile ID, and registry reference; supply
only the image digest and the command to run.

Create a separate Application-scoped API key with only `image.read`, using
**Personal access tokens**. In Bash on a runner with `curl` and `jq`, read the
key without adding it to shell history:

```bash
read -r -s -p "Deployment read key: " ORBIT_READ_KEY
printf '\n'
export ORBIT_READ_KEY
read -r -p "Preview build's full sha256: digest: " IMAGE_DIGEST

sh /path/to/orbit-image-guard.sh "$IMAGE_DIGEST" \
  python3 -c 'import os; print("Command ran with", os.environ["ORBIT_IMAGE_REFERENCE"])'
```

Replace the script path with the file you saved. This command only prints the
approved image reference. It should execute for the passing Preview build and
use `repository@sha256:…`, never a mutable tag. Keep the same digest for the
policy-change exercise below.

## Change the requirements, then reassess — policy manager and requester

1. In **Edit profiles**, change Preview's regression entry from **Excluded**
   to **Required**, then **Save profiles**. Keep the check definition unchanged.
2. Refresh the Preview build. Its historical assessment still says
   **Requirements met** for the saved requirements. **Current policy** denies
   Preview because the newly required check has no qualifying result.
3. Rerun the guard above. It must exit nonzero without printing `Command ran
   with`. A previous pass does not authorize a deployment under new requirements.
4. As an image reader with `image_validation_request`, open **Details → Profile
   assessments** and choose **Reassess under current policy** on this source's
   current, non-superseded assessment. Orbit creates a new assessment on the same
   digest. It requests fresh smoke
   and regression checks; it does not copy the earlier smoke result.
5. Wait for those checks to pass, then reload. The old assessment remains in
   history, the new one is current, and Preview is **Allowed by current policy**.
   The guard now executes the printing command again without another build/push.

Optionally rename Preview to **Review** and save. Its stable profile identity
remains, so the copied guard still targets it and compatible evidence stays
eligible. A new profile with the same display name would have a different ID.

For a real deployment, replace the printing command with your deployment script
and have it consume `ORBIT_IMAGE_REFERENCE`. Your CI/CD system owns approvals,
deployment credentials, rollout, and rollback. Run the guard immediately before
that command. Its decision is current at the check time; it does not lock a
rollout or prevent another deployment path from bypassing your CI workflow.

## Compare audiences

An ordinary member has no image access by default. Grant only the permissions
needed when comparing views with a second account:

| Audience | Expected behavior |
|---|---|
| Image reader (`image_read`) | Browse builds, source, assessment history, current decisions, and guard setup; cannot change profiles or request a reassessment |
| Requester (`image_read` + `image_validation_request`) | Reader view plus reassessment and validation requests; cannot edit policy |
| Policy manager (`image_read` + `image_validation_policy_manage`) | Edit named profiles, checks, and source rules; requesting results is a separate authority |
| CI-connection or hook manager | Respective setup controls with image-read authority; these permissions do not grant all validation actions |

Image-only members currently cannot discover Applications through the tenant
catalog. Share the exact Images URL for this audience check. The customer from
the package chapter does not gain image access from buying the billing engine.

## Finish or keep the demo

When finished, stop your demo receiver and revoke the demo validation API key,
deployment-read key, and unused publisher keys/connections in Orbit. Disabling
a CI connection pauses publishing; revoking the connection also makes its
source unusable for new eligibility decisions. Accepted validation results remain
in history after a reporting key is revoked.

```bash
unset ORBIT_READ_KEY
unset REGISTRY_API_KEY_FILE
```

Keep the receiver database if you will resume. Remove only this demo's local
secret files when retiring it. Remove any temporary runner registration or hook
endpoint you created for the tutorial. Keep the registry hidden to inspect its
history, or use **Delete registry** when you are done with the entire sandbox.

Removing an Application from the accepted workspace archives its storage and
cancels queued validation deliveries. Orbit does not claim to cancel an external
job that was already admitted. Re-adding the Application creates a new identity
and new storage; deletion is not a pause/resume control.

**Result:** you have exercised automatic image discovery, trusted publishing
connections, custom validation profiles, external checks, current-policy
decisions, reassessment, and an exact-digest command guard. Application rollout,
Launchpad changelog links, and related package-build tracking are separate future
integrations; the pool does not claim to provide them.

**Next: [Use your own workspace](../your-workspace.md).**
