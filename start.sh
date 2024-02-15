#!/bin/sh

/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
/app/tailscale up --authkey=${TAILSCALE_AUTHKEY} --hostname=go

/app/tailscale serve --bg --http=80 8000
gunicorn -b 0.0.0.0 go_ji:app
