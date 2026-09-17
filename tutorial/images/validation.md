# Configure automatic validation

Create two profiles for the billing Application. These are names you choose,
not built-in deployment environments. Both profiles validate the exact pushed
image; Release requires one additional check.

## Define the checks and source rules — owner

Open **Images → Validation profiles → Edit profiles**. Add these checks with
the definitions below. Leave baseline empty and parameters as `{}`. The supplied
validator implements version `1` of these workflows and refuses other definitions.

| Key | Name | Workflow | Version | What actually runs |
|---|---|---|---|---|
| `smoke` | API smoke | `meridian/billing-smoke` | `1` | Start the image's normal entrypoint, call its health and invoice API, check installed package versions |
| `regression` | Billing regression | `meridian/billing-regression` | `1` | Run the invoice and ledger tests against the wheels installed inside the image |

Add profiles and set every check's requirement:

| Profile | API smoke | Billing regression |
|---|---|---|
| **Preview** | Required | Excluded |
| **Release** | Required | Required |

Add ordered rules, selecting your **Meridian publishing** connection in each:

| Order | Source kind | Ref pattern | Event | Profile |
|---|---|---|---|---|
| 1 | Branch | `refs/heads/main` | `push` | Release |
| 2 | Branch | `refs/heads/*` | `push` | Preview |

Save profiles and note the policy revision. The first matching rule wins. If
you started from **Add starter presets**, replace its checks and rules with these
demo definitions. In particular, presets leave a generic publisher's main branch
unclassified until you explicitly authorize it; do not rely on a later wildcard
rule to make that decision.

Git tags use separate `refs/tags/…` rules. A pull request targeting main is still
a pull request. Docker tags do not select profiles. You can extend the rules
later; the workflow in this tutorial publishes branch pushes only.

## Connect an external validator

This path uses Orbit's shipped signed-webhook receiver and reporting adapter,
with Meridian's real checks replacing the sample check. It needs no Buildkite
subscription. The receiver runs the commands on your Docker runner; your team can
later replace it with a webhook integration that starts your chosen CI workflow.

On the validation runner, check out this demo revision and run `./demo setup`
(or use `--source /path/to/orbit` with the matching Orbit checkout). Then:

```bash
export VALIDATOR_TOOLS="$HOME/.local/share/meridian-validator"
./demo validation-tools --out "$VALIDATOR_TOOLS"
```

The helper installs the receiver, reporting adapter, and
`meridian-validation.sh`. It starts no service and refuses to overwrite an
existing destination. Keep the copied tools outside the CI checkout so a later
checkout or cleanup does not replace a running validator.

### Give the validator only this Application

In **Personal access tokens**, create an **Application**-scoped key for
`billing-api` with `image.push` and `image.validation.report`, and a bounded
expiry. The reference adapter needs `image.push` to obtain its own Docker login
for the private image; a report-only key cannot do that. This is an ordinary
`dpr_` API key, separate from a `dpk_` CI publisher key or a GitHub ID token.

In a Bash shell on the validator, keep it in a private file:

```bash
umask 077
export VALIDATOR_STATE="$HOME/.local/state/meridian-validator"
mkdir -p "$VALIDATOR_STATE"
chmod 700 "$VALIDATOR_STATE"
read -r -s -p "Validation API key: " MERIDIAN_VALIDATION_KEY
printf '\n'
printf '%s' "$MERIDIAN_VALIDATION_KEY" > "$VALIDATOR_STATE/report-key"
unset MERIDIAN_VALIDATION_KEY

python3 - "$VALIDATOR_STATE/signing-secret" <<'PY'
from pathlib import Path
import secrets, sys
with Path(sys.argv[1]).open("x") as destination:
    destination.write(secrets.token_hex(32))
PY
```

Keep an existing signing-secret file on restart; do not regenerate it. Open that
file privately to copy its value into the hook form below. Do not put these two
secrets in the repository or in command arguments.

### Start the receiver and save the hook

Use your own tenant and Application UUIDs recorded on the Images page:

```bash
export REGISTRY_URL=https://orbit-staging.home.costanga.com
# Set REGISTRY_TENANT and ORBIT_APPLICATION_ID to your own UUIDs.
export REGISTRY_API_KEY_FILE="$VALIDATOR_STATE/report-key"
python3 "$VALIDATOR_TOOLS/receiver/orbit_webhook_receiver.py" \
  --secret-file "$VALIDATOR_STATE/signing-secret" \
  --database "$VALIDATOR_STATE/deliveries.sqlite3" \
  --tenant "$REGISTRY_TENANT" \
  --application "$ORBIT_APPLICATION_ID" \
  -- "$VALIDATOR_TOOLS/meridian-validation.sh"
```

Keep it running for this chapter. It listens on `127.0.0.1:8787`; put your existing,
operator-approved HTTPS endpoint in front of it. The hook URL must reach this
receiver from Orbit, not the browser's localhost. For private destinations, the
operator must explicitly allow the receiver's network. The shipped adapter is a
reference integration, not a managed production webhook service.

In **Images → Validation hooks**, add a **Webhook** hook named `Meridian checks`.
Set that endpoint, enter validation keys `smoke, regression`, and enter the signing
secret. Choose **Create hook**, then **Check connection**. A successful signed ping
checks connectivity without running a validation. In **Validation profiles**,
confirm that both saved checks show their enabled hook destination.

Orbit retains request/delivery identity and retries delivery. The receiver
retains a private SQLite record so a duplicate delivery does not create another
execution. Keep its database across restarts. The adapter reads the requested
validation UUID and definition from Orbit, pulls the exact digest, runs the
check, then reports the real exit result with authentication. It does not select
the newest image or borrow another assessment's passing result.

## Push main and a feature build

Now commit and push the publishing workflow prepared on the previous page from
your fork's main branch:

```bash
git add .github/workflows/ci.yml
git commit -m "ci: publish billing images through Orbit"
git push origin main
```

Watch the package-build job, then the publishing job. Open **Images → Build pool**:
the digest appears automatically, its source arrives, and **Release** requests
both checks. Each check must finish successfully before the assessment says
**Requirements met**. No per-build registration or manual request is necessary.

For Preview, create a branch from this main revision:

```bash
git switch -c demo/image-preview
git commit --allow-empty -m "demo: exercise the Preview image profile"
git push -u origin demo/image-preview
```

The new source selects **Preview**: smoke runs, regression is **Excluded**.
The image includes its input manifest, so this new commit produces a distinct
demo image even without a source edit. In general, identical images can share
one digest with multiple source associations; Orbit preserves each assessment.

**Excluded** records an intentional profile choice. It is different from a
required check reporting **Skipped**, which does not satisfy the profile. A
failed check shows **Failed**; a hook accepting delivery is not a test pass.
The earlier CI unit tests are build-time evidence; these checks exercise the
image and its installed dependencies after the image exists.

**Result:** a Release build with two passing checks, and a Preview build with a
passing smoke check and an explicitly excluded regression check.

**Next: [Inspect decisions and reassess](decisions.md).**
