# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.15-alpine@sha256:a0f2e268f2ce8f3709611a90054ec6a8ae31f6251f5896b8648b9bb99835e30a
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY uv.lock pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    pip3 install --no-deps uv==0.8.4 && \
    uv sync --frozen --no-dev

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:ed6480b33c6eb67c9cbd203ed42b9fb57e361986725b6856def71b7a3d9e276c /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:ed6480b33c6eb67c9cbd203ed42b9fb57e361986725b6856def71b7a3d9e276c /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
