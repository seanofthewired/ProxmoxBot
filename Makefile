# Configuration
PROJECT_NAME = bot

# Specify your docker-compose file if not the default docker-compose.yml
COMPOSE_FILE = docker-compose.yml

.PHONY: all clean test coverage report serve-report lint format build up down

# Define a standard set of tasks to run by default
all: build lint test coverage

# Clean up Python bytecode and test artifacts
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf src/.pytest_cache
	rm -rf src/htmlcov
	rm -f src/.coverage

# Run tests using Docker Compose
test: build
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) pytest tests/

# Generate coverage report using Docker Compose
coverage: build
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) pytest --cov=$(PROJECT_NAME) tests/

# Generate HTML coverage report using Docker Compose
report: build
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) pytest --cov=$(PROJECT_NAME) --cov-report html tests/

serve-report: report
	@cd src/htmlcov && python3 -m http.server 8000

# Lint the project using Docker Compose
lint: build
	docker compose run --rm $(PROJECT_NAME) flake8 $(PROJECT_NAME) tests/

# Format the project source code using Docker Compose
format: build
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) black $(PROJECT_NAME) tests/
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) isort $(PROJECT_NAME) tests/
	docker compose run --rm -v $$(pwd)/src:/app $(PROJECT_NAME) autopep8 --in-place --recursive $(PROJECT_NAME) tests/

# Build the Docker containers using Docker Compose
build: clean
	docker compose build

# Spin up the Docker containers using Docker Compose
up:
	docker compose up -d

# Shut down the Docker containers and remove them using Docker Compose
down:
	docker compose down
