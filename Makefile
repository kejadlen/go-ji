all: requirements.txt dev-requirements.txt

.PHONY: dev
dev:
	fd ".*.(html|py)$$" | entr -r flask --app go_ji run

.PHONY: upgrade-deps
upgrade-deps:
	pip-compile --upgrade

requirements.txt: pyproject.toml
	pip-compile --output-file=requirements.txt pyproject.toml

dev-requirements.txt: pyproject.toml
	pip-compile --extra=dev --output-file=dev-requirements.txt pyproject.toml
