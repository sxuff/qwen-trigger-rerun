FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl wget jq procps iproute2 ca-certificates && rm -rf /var/lib/apt/lists/*  && pip install --no-cache-dir pyyaml  && useradd -m -u 1000 analyst && mkdir -p /workspace && chown analyst:analyst /workspace
USER analyst
WORKDIR /workspace
