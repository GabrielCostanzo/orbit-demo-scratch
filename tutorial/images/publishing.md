# Connect publishing once

The package-build job already preserves the exact tested wheels. Add an image
publishing job that downloads those artifacts and uses Orbit's generated
connection configuration. Configure validation on the next page **before
pushing the workflow change**, so the first source report receives a profile.

## GitHub Actions — the tutorial path

1. Open **Images → CI connections → Connect CI**. Name the connection
   `Meridian publishing` and choose **GitHub Actions · workload identity**.
2. Enter your fork's repository and approved workflow file, for example
   `your-account/orbit-demo/.github/workflows/ci.yml`. Use your actual fork,
   including case. The workflow file identity applies to main and feature runs;
   branch selection belongs in validation profiles.
3. Create the connection and select **Copy configuration**. Add its generated
   `orbit_publish` job under the existing `jobs:` in `.github/workflows/ci.yml`.
   Keep `build-and-test`. Do not add a second `jobs:` key.
4. Add these job-level fields to `orbit_publish`:

   ```yaml
   needs: build-and-test
   if: github.event_name == 'push'
   ```

   Keep its generated permissions, including `id-token: write`. Its self-hosted
   runner must be your trusted runner with access to Orbit and the image registry.
   This demo publishes branch pushes; pull requests still run the existing
   package tests, but do not execute this publishing job.
5. After the generated checkout step and **before** the Orbit session/login/build
   steps, insert these steps:

   ```yaml
   - name: Install uv
     uses: astral-sh/setup-uv@v6
     with:
       version: "0.11.28"

   - name: Download this run's tested distributions
     uses: actions/download-artifact@v4
     with:
       name: meridian-distributions
       path: ${{ runner.temp }}/meridian-distributions

   - name: Reuse the exact wheels in the image
     run: ./demo image-context --artifacts "$RUNNER_TEMP/meridian-distributions"
   ```

   The helper checks the current commit, repository, run, attempt, filenames,
   sizes, and hashes. It copies five wheels into `.orbit-image-context`, which
   the root Dockerfile consumes. A retry that only reruns the image job after
   the attempt number changes is refused: rerun all jobs instead.
6. Keep the generated steps that report the successful push digest and source
   context and end the publishing session on success or failure. Use a dedicated
   runner, or an isolated `DOCKER_CONFIG` for this job, so another Application's
   Docker login is not overwritten.

You do not add `registry images register` to every build. Discovery creates the
build; the generated connection code attaches the publishing source and run.
If source arrives before discovery, Orbit joins them when the digest appears.

## Other CI systems

Choose **Generic CI · publisher key** instead, then **Create publisher key**.
Store the one-time secret as `ORBIT_PUBLISHER_KEY` in your CI secret store and
copy the generated shell configuration. Run it from this repository's producer
checkout after preparing `.orbit-image-context` from that job's tested artifacts.
Use `./demo build --out /empty/artifact/path` once and reuse its outputs for both
image construction and your package publishing process.

Map the generated script's `ORBIT_*` variables to the real repository, checkout
commit, full branch or tag ref, event, run, attempt, and distinct producer job.
Buildkite mappings are included; other providers map them once. Do not describe
a manual or scheduled job as `push` to make it match a rule.

Generic connections record **Publisher asserted** context. GitHub OIDC records
**Provider verified** trigger context and separately reported checkout context.
Neither is a claim that Orbit independently proved the source produced the image
bytes. Approve only the publishing connection you intend to trust in the source
rules on the next page.

The earlier `./demo publish` package helper specifically retrieves GitHub
artifacts. This generic image path does not turn that helper into a multi-provider
package release tool.

**Result:** the one-time publishing configuration is ready in your working tree.
Save profiles and hooks before committing and pushing it.

**Next: [Configure validation](validation.md).**
