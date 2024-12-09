# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.13-alpine@sha256:804ad02b9ba67ea1f8307eeb6407b121c6bd6bb19d3f182aae166821eb59d6a4
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:da35f0fbeb3037754049e3b079cb30c58c140576a50b54be107c0ff6ad0ec0e9 /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:da35f0fbeb3037754049e3b079cb30c58c140576a50b54be107c0ff6ad0ec0e9 /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
