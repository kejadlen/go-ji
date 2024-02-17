#!/bin/sh

mkdir -p /data/tailscale
/app/tailscaled --state=/data/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=${TAILSCALE_HOSTNAME}
/app/tailscale serve reset
/app/tailscale serve --http=80 8000
