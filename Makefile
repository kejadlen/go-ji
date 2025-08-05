all: uv.lock

.PHONY: dev
dev:
	fd ".*.(html|py)$$" | entr -r flask --app go_ji run --debug --port $$PORT

.PHONY: tailscale
tailscale:
	tailscale serve --bg $$PORT

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
		--cap-add NET_ADMIN \
		--device /dev/net/tun \
		--env-file .env.dev \
		--name go_ji \
		--publish 8000:8000 \
		--rm \
		go-ji

.PHONY: upgrade-deps
upgrade-deps:
	uv lock --upgrade

uv.lock: pyproject.toml
	uv lock
