# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.13-alpine@sha256:b6f01a01e34091438a29b6dda4664199e34731fb2581ebb6fe255a2ebf441099
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:9d4c17a8451e2d1282c22aee1f08d28dc106979c39c7b5a35ec6313d4682a43e /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:9d4c17a8451e2d1282c22aee1f08d28dc106979c39c7b5a35ec6313d4682a43e /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
