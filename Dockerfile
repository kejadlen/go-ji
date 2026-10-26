# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.15-alpine@sha256:d44b1254cb92329418d164b22b20d86bbd3869d48e80e09e476531a409a728bb
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY uv.lock pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    pip3 install --no-deps uv==0.8.4 && \
    uv sync --frozen --no-dev

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:b11583ad2e93e4671128538c88cf11f460444a5d7e449311dd1933a400ab849d /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:b11583ad2e93e4671128538c88cf11f460444a5d7e449311dd1933a400ab849d /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
