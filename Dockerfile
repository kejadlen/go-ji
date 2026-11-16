# https://tailscale.com/kb/1132/flydotio
# https://github.com/docker/awesome-compose/blob/master/flask/app/Dockerfile

FROM python:3.15-alpine@sha256:0f9552bb28711333da16915ec146f5e6bb44a7fdac9ced15dc17c2e0206346dd
RUN apk update && apk add ca-certificates iptables ip6tables supervisor && rm -rf /var/cache/apk/*

WORKDIR /app

COPY uv.lock pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/uv \
    pip3 install --no-deps uv==0.8.4 && \
    uv sync --frozen --no-dev

COPY . /app

# Copy Tailscale binaries from the tailscale image on Docker Hub.
COPY --from=docker.io/tailscale/tailscale:stable@sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4 /usr/local/bin/tailscaled /app/tailscaled
COPY --from=docker.io/tailscale/tailscale:stable@sha256:72c1e19e0aedca96b8533bbb0b4368564410ff20b17e53b804eb6c1f04a31be4 /usr/local/bin/tailscale /app/tailscale
RUN mkdir -p /var/run/tailscale /var/cache/tailscale /var/lib/tailscale

ENV GO_JI_DB_URL sqlite:////data/go-ji.db

# Run on container startup.
CMD supervisord -c /app/docker/supervisor.conf
