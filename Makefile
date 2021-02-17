# Variables

SERVICE_NAME=vacina-manaus-backend

LATEST_PDF=$(shell ls -t1 data/raw/ |  head -n 1)

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
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/download_data.py

.PHONY: split-pdf
split-pdf:
	@mkdir -p tmp/pdf
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} \
		pdftk data/raw/${LATEST_PDF} burst output tmp/pdf/page-%d.pdf

.PHONY: extract-data
extract-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/extract_data.py

.PHONY: concatenate-csv
concatenate-csv:
	@cat tmp/csv/*.csv > data/cleaned/${shell echo ${LATEST_PDF} | cut  -d "." -f1}.csv
	@rm -rf tmp

.PHONY: process-data
process-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/process_data.py

.PHONY: process-main
process-main:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/main.py

.PHONY: lint
lint:
	@docker run --rm -v $(shell pwd):/apps alpine/flake8:3.8.4 --config=.flake8 $(shell find src/*.py)
