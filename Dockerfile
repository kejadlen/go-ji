# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.14-alpine@sha256:016508ba505da24f7139765bc4bb669df4e88eb2f12eeadd571bf2f88d7533df
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY uv.lock pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    pip3 install --no-deps uv==0.8.4 && \
    uv sync --frozen --no-dev

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:2667499ed87ae29218f292556ba062918402dd5e92e93637af14867e4df12dd3 /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:2667499ed87ae29218f292556ba062918402dd5e92e93637af14867e4df12dd3 /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
