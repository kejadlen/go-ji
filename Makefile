all: requirements.txt dev-requirements.txt

.PHONY: dev
dev:
	fd ".*.(html|py)$$" | entr -r flask --app go_ji run

.PHONY: docker
docker:
	docker build -t go-ji .
	docker run \
		--cap-add=NET_ADMIN \
		--device=/dev/net/tun \
		-e=TAILSCALE_AUTHKEY=$$TAILSCALE_AUTHKEY \
		go-ji

.PHONY: upgrade-deps
upgrade-deps:
	pip-compile --upgrade

requirements.txt: pyproject.toml
	pip-compile --output-file=requirements.txt pyproject.toml

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
