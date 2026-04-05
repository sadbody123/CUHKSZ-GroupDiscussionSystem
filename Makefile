.PHONY: install test validate-env smoke run-api run-ui docker-up bootstrap-dev-snapshot

install:
	python -m pip install -e ".[dev]"

bootstrap-dev-snapshot:
	python main.py bootstrap-dev-snapshot

test:
	python -m pytest

validate-env:
	python main.py validate-env

smoke:
	python main.py run-smoke --snapshot-id dev_snapshot_v2 --topic-id tc-campus-ai --provider mock --runtime-profile default

run-api:
	python main.py run-api --host 127.0.0.1 --port 8000

run-ui:
	python main.py run-ui --api-base-url http://127.0.0.1:8000

docker-up:
	docker compose -f docker/docker-compose.yml up --build
