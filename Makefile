all: requirements.txt dev-requirements.txt

.PHONY: dev
dev:
	tailscale serve --bg 5000
	fd ".*.(html|py)$$" | entr -r flask --app go_ji run --debug

.PHONY: test
test:
	coverage run -m pytest

.PHONY: docker
docker:
	docker build -t go-ji .
	docker run \
		--cap-add=NET_ADMIN \
		--device=/dev/net/tun \
		--name=go_ji \
		--publish 8000:8000 \
		--rm \
		-e=GO_JI_SENTRY_DSN=$$GO_JI_SENTRY_DSN \
		-e=GO_JI_SENTRY_ENVIRONMENT=development \
		-e=TAILSCALE_AUTHKEY=$$TAILSCALE_AUTHKEY \
		-e=TAILSCALE_HOSTNAME=$$TAILSCALE_HOSTNAME \
		go-ji

.PHONY: upgrade-deps
upgrade-deps:
	pip-compile --upgrade

requirements.txt: pyproject.toml
	pip-compile --output-file=requirements.txt pyproject.toml

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
