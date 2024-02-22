all: requirements.txt dev-requirements.txt

.PHONY: dev
dev:
	fd ".*.(html|py)$$" | entr -r flask --app go_ji run --debug --port 5001

.PHONY: tailscale
tailscale:
	tailscale serve --bg 5001

.PHONY: lint
lint:
	ruff check .
	ruff format --check .
	# alembic upgrade head && alembic check

.PHONY: test
test:
	coverage run -m pytest
	coverage report

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

dev-requirements.txt: pyproject.toml requirements.txt
	pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
