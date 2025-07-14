# Default target
.PHONY: help
help:
	@echo "Usage: make [target] APP=<app>"
	@echo "Available apps: bookstack, invoiceninja, indico, prestashop"
	@echo "Targets:"
	@echo "  up         - Start the app"
	@echo "  down       - Stop and remove"
	@echo "  status     - Check the status of all apps"
	@echo "  seed       - Seed the database with sample data"

# Validate app parameter
.PHONY: validate-app
validate-app:
	@if [ -z "$(APP)" ]; then \
		echo "Error: APP parameter is required. Use make help for usage information."; \
		exit 1; \
	fi
	@case "$(APP)" in \
		bookstack|invoiceninja|indico) ;; \
		*) echo "Error: Invalid app '$(APP)'. Available apps: bookstack, invoiceninja, indico, prestashop"; exit 1 ;; \
	esac

# Define colors for shell output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m

# Define image hashes directly
BOOKSTACK_IMAGES = cd4ffcc33ab2
INVOICENINJA_IMAGES = f015ee8f926d
INDICO_IMAGES = 129d29d02710
PRESTASHOP_IMAGES = 6dd4567d11f4

# Check Docker and Docker Compose
.PHONY: check-docker
check-docker:
	@if ! command -v docker > /dev/null; then \
		echo "Error: Docker is not installed. Please install it and try again."; \
		exit 1; \
	fi
	@if ! command -v docker compose > /dev/null; then \
		echo "Error: Docker Compose is not installed. Please install it and try again."; \
		exit 1; \
	fi

# Check if app is running
.PHONY: is-running
is-running: check-docker validate-app
	@app_running=false; \
	images=""; \
	case "$(APP)" in \
		bookstack) images="$(BOOKSTACK_IMAGES)" ;; \
		invoiceninja) images="$(INVOICENINJA_IMAGES)" ;; \
		indico) images="$(INDICO_IMAGES)" ;; \
		prestashop) image="$(PRESTASHOP_IMAGES)" ;; \
	esac; \
	for image in $$images; do \
		container_id=$$(docker ps --filter "ancestor=$$image" --format "{{.ID}}" 2>/dev/null); \
		if [ -n "$$container_id" ]; then \
			app_running=true; \
			break; \
		fi; \
	done; \
	if $$app_running; then \
		echo "true"; \
	else \
		echo "false"; \
	fi

# Start an app
.PHONY: up
up: check-docker validate-app
	@compose_path="./${APP}/docker-compose.yaml"; \
	if [ -z "$$compose_path" ]; then \
		echo "Error: Compose file path not found for app $(APP)"; \
		exit 1; \
	fi; \
	running=$$(make is-running APP=$(APP)); \
	if [ "$$running" = "true" ]; then \
		echo "$(APP) is already running. Use 'make down APP=$(APP)' to stop it first."; \
		exit 0; \
	fi; \
	echo "Starting $(APP)..."; \
	docker compose -f "./$(APP)/docker-compose.yaml" up -d; \
	echo "$(APP) deployed successfully!"; \
	echo "To seed the database with sample data, run: make seed APP=$(APP)"

# Seed the database with sample data
.PHONY: seed
seed: check-docker validate-app
	@compose_path="./${APP}/docker-compose.yaml"; \
	if [ -z "$$compose_path" ]; then \
		echo "Error: Compose file path not found for app $(APP)"; \
		exit 1; \
	fi; \
	running=$$(make is-running APP=$(APP)); \
	if [ "$$running" = "false" ]; then \
		echo "$(APP) is not running. Please start it first with: make up APP=$(APP)"; \
		exit 1; \
	fi; \
	echo "Seeding database for $(APP)..."; \
	case "$(APP)" in \
		bookstack) \
			docker exec -it bookstack-app-1 /bin/bash -c "cd /app/www && php artisan db:seed --class=DummyContentSeeder"; \
			;; \
		invoiceninja) \
			docker compose -f "$$compose_path" run --rm app php artisan db:seed --class=RandomDataSeeder; \
			;; \
		prestashop) \
			echo "No action required."; \
			;; \
		
	esac; \
	echo "Database seeding completed for $(APP)!"

# Stop and remove an app
# Delete all associated volumes
.PHONY: down
down: check-docker validate-app
	@compose_path="./${APP}/docker-compose.yaml"; \
	if [ -z "$$compose_path" ]; then \
		echo "Error: Compose file path not found for app $(APP)"; \
		exit 1; \
	fi; \
	running=$$(make is-running APP=$(APP)); \
	if [ "$$running" = "false" ]; then \
		echo "$(APP) is not running."; \
		exit 0; \
	fi; \
	echo "Stopping and removing $(APP)..."; \
	docker compose -f "./$(APP)/docker-compose.yaml" down -v --remove-orphans; \

# Check status of all apps 
# 1. online - all containers healthy
# 2. partial - some containers down
# 3. offline - all containers down
.PHONY: status
status: check-docker
	@echo "App Status:"
	@for app in bookstack invoiceninja saleor wagtail; do \
		all_running=true; \
		any_running=false; \
		container_ids=$$(docker ps --filter "name=^/${app}" --format "{{.ID}}"); \
		if [ -z "$$container_ids" ]; then \
			all_running=false; \
		else \
			for cid in $$container_ids; do \
				health_status=$$(docker inspect --format '{{.State.Health.Status}}' "$$cid" 2>/dev/null || echo "nohealth"); \
				container_status=$$(docker inspect --format '{{.State.Status}}' "$$cid" 2>/dev/null || echo "unknown"); \
				if [ "$$health_status" = "healthy" ] || [ "$$container_status" = "running" ]; then \
					any_running=true; \
				else \
					all_running=false; \
				fi; \
			done; \
		fi; \
		printf "  %-15s " "$$app"; \
		if $$any_running; then \
			if $$all_running; then \
				printf "${GREEN}online${NC}\n"; \
			else \
				printf "${YELLOW}unhealthy${NC}\n"; \
			fi; \
		else \
			printf "${RED}offline${NC}\n"; \
		fi; \
	done