FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1
WORKDIR /app

# ./demo image-context supplies the wheels already tested by the package job.
# The image does not resolve packages from a moving staging/production index.
COPY .orbit-image-context/wheels/ /tmp/wheels/
RUN python -m pip install --no-cache-dir --no-index --no-deps /tmp/wheels/*.whl \
    && rm -r /tmp/wheels
COPY .orbit-image-context/inputs.json /app/build-inputs.json
COPY project/billing/application/billing-api/server.py /app/server.py
COPY project/billing/application/billing-api/checks.py /app/checks.py
COPY examples/invoices.json /app/examples/invoices.json
COPY tests/test_billing.py /app/tests/test_billing.py

USER 65534:65534
EXPOSE 8080
CMD ["python", "/app/server.py"]
