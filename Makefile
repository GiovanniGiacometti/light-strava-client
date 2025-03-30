dev-sync:
	uv sync --all-extras --cache-dir .uv-cache

prod-sync:
	uv sync --no-dev --cache-dir .uv-cache

lint:
	uv run ruff format
	uv run ruff check --fix
	uv run mypy --install-types --non-interactive --package strava_client

test:
	uv run pytest --verbose --color=yes tests

validate: lint test

publish:
	# Use it like: make publish VERSION_TAG=0.0.1
	# The __version__ variable in strava_client/__init__.py must be updated manually as of now.
	# The build tool retrieves it from there.
	git tag -a v$(VERSION_TAG) -m "Release v$(VERSION_TAG)"
	git push origin v$(VERSION_TAG)