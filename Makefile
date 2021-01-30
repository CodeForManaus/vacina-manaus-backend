# Variables

SERVICE_NAME=vacina-manaus-backend

.PHONY: all
all: build data

.PHONY: build
build:
	@docker-compose build --pull

.PHONY: build-no-cache
build-no-cache:
	@docker-compose build --no-cache

.PHONY: data
data: download-data extract-data process-data

.PHONY: download-data
download-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python download_data.py

.PHONY: extract-data
extract-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python extract_data.py

.PHONY: process-data
process-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python process_data.py

.PHONY: process-main
process-main:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python main.py

.PHONY: lint
lint:
	@docker run --rm -v $(shell pwd):/apps alpine/flake8:3.8.4 --config=.flake8 $(shell find *.py)
