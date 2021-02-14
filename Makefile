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
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/download_data.py

.PHONY: split-pdf
split-pdf:
	$(eval NUM_CORES := $(shell grep -c ^processor /proc/cpuinfo))
	$(eval LATEST_PDF := $(shell ls -t1 data/raw/ |  head -n 1))
	$(eval NUM_PAGES := $(shell \
		docker-compose run --user=$$(id -u) --rm \
			$(SERVICE_NAME) pdfinfo data/raw/${LATEST_PDF} \
		| grep Pages | cut -d ":" -f2 | tr -d '[:space:]'))
	$(eval CHUNK := \
		$(shell \
			chunk=$$(($(NUM_PAGES) / $(NUM_CORES))); \
			last_chunk=$$((chunk * $(NUM_CORES))); \
			if [ $$last_chunk -lt $(NUM_PAGES) ]; then \
				echo $$((chunk + 1)); \
			else \
				echo $$chunk; \
			fi))
	$(info The file $(LATEST_PDF) has $(NUM_PAGES) pages)
	$(info and it will be split into $(NUM_CORES) chucks of $(CHUNK) pages.)
	$(shell \
		mkdir -p tmp/pdf; \
		for i in $$(seq 0 $$(($(NUM_CORES) -1))); do \
			start=$$((i * $(CHUNK) + 1)); \
			if [ $$(($$i + 1)) -lt $(NUM_CORES) ]; then \
				last=$$((i * $(CHUNK) + $(CHUNK))); \
			else \
				last=$(NUM_PAGES); \
			fi; \
			docker-compose run --user=$$(id -u) --rm \
				$(SERVICE_NAME) pdftk data/raw/$(LATEST_PDF) cat "$$start-$$last" output tmp/pdf/chunk-$$i.pdf; \
		done)

.PHONY: extract-data
extract-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/extract_data.py

.PHONY: process-data
process-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/process_data.py

.PHONY: process-main
process-main:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/main.py

.PHONY: lint
lint:
	@docker run --rm -v $(shell pwd):/apps alpine/flake8:3.8.4 --config=.flake8 $(shell find src/*.py)
