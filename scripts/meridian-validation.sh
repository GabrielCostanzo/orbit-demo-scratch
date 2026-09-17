#!/bin/sh
# Called by Orbit's reference reporting adapter, or the equivalent external CI.
set -eu
: "${ORBIT_IMAGE:?The reporting adapter must provide the exact pulled image reference}"
: "${ORBIT_VALIDATION_KEY:?The request must identify smoke or regression}"
: "${ORBIT_VALIDATION_DEFINITION_SHA256:?The request must include the check definition digest}"
python3 - <<'PY'
import hashlib, json, os, re
if not re.fullmatch(r"[A-Za-z0-9][^@\s]*@sha256:[0-9a-f]{64}", os.environ["ORBIT_IMAGE"]):
    raise SystemExit("Meridian validation requires a digest-qualified image, not a tag")
key = os.environ["ORBIT_VALIDATION_KEY"]
if key not in {"smoke", "regression"}:
    raise SystemExit("Unknown Meridian check: " + key)
definition = {"workflow": "meridian/billing-" + key, "version": "1", "parameters": {}}
expected = hashlib.sha256(json.dumps(definition, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if os.environ["ORBIT_VALIDATION_DEFINITION_SHA256"] != expected:
    raise SystemExit("Unsupported Meridian check definition; use the workflow/version/parameters in tutorial/images/validation.md")
PY

case "$ORBIT_VALIDATION_KEY" in
  smoke)
    container=$(docker run --detach --pull=never --network none --read-only \
      --cap-drop ALL --security-opt no-new-privileges --user 65534:65534 \
      --memory 128m --cpus 1 --pids-limit 64 "$ORBIT_IMAGE")
    cleanup() { docker rm --force "$container" >/dev/null; }
    trap cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    # Exercise the image's normal entrypoint, then inspect its actual HTTP API.
    docker exec "$container" python /app/checks.py smoke
    ;;
  regression)
    docker run --rm --pull=never --network none --read-only --cap-drop ALL \
      --security-opt no-new-privileges --user 65534:65534 --memory 128m \
      --cpus 1 --pids-limit 64 --tmpfs /tmp:rw,noexec,nosuid,size=16m \
      "$ORBIT_IMAGE" python /app/checks.py regression
    ;;
  *) printf '%s\n' "Unknown Meridian check: $ORBIT_VALIDATION_KEY" >&2; exit 2 ;;
esac
