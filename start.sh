#!/bin/sh

mkdir -p /data/tailscale
/app/tailscaled --state=/data/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=go

# trap '/app/tailscale logout' INT

/app/tailscale serve --bg --http=80 8000
gunicorn --daemon --bind 0.0.0.0:8000 go_ji:create_app

wait "$!"
