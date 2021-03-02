# Variables

SERVICE_NAME=vacina-manaus-backend

SHELL=/usr/bin/env bash
LATEST_CSV=data/cleaned/${shell echo ${LATEST_PDF} | cut  -d "." -f1}.csv
LATEST_PDF=$(shell ls -t1 data/raw/ |  head -n 1)
NUM_CHUNKS=$(shell ls tmp/csv/*.csv | wc -l)

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

.PHONY: extract-data
extract-data: split-pdf run-extract-data concatenate-csv

.PHONY: run-extract-data
run-extract-data:
	$(info Running extract_data.py...)
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/extract_data.py

.PHONY: split-pdf
split-pdf:
	$(info Splitting the pdf ${LATEST_PDF} into pages...)
	@mkdir -p tmp/pdf
	@docker-compose run --user=$(shell id -u) -e JAVA_OPTS="-Xmx2048m" --rm ${SERVICE_NAME} \
		pdftk data/raw/${LATEST_PDF} burst output tmp/pdf/page-%d.pdf

.PHONY: concatenate-csv
concatenate-csv:
	$(info Concatenating all csv files into ${LATEST_CSV}...)
	@eval cat tmp/csv/page-{1..${NUM_CHUNKS}}.csv > ${LATEST_CSV}

.PHONY: process-data
process-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/process_data.py

.PHONY: process-main
process-main:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/main.py

.PHONY: lint
lint:
	@docker run --rm -v $(shell pwd):/apps alpine/flake8:3.8.4 --config=.flake8 $(shell find src/*.py)
