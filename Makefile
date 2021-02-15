# Variables

SERVICE_NAME=vacina-manaus-backend

COMPRESSED_FILE_ROOT_DIR=data/compressed
DECOMPRESSED_FILE_DIR=data/decompressed

LATEST_COMPRESSED_FILE_ROOT_DIR=$(shell ls ${COMPRESSED_FILE_ROOT_DIR} | tail -n 1)
LATEST_DECOMPRESSED_FILE=$(shell ls ${DECOMPRESSED_FILE_DIR} | tail -n 1)

FILE_TO_COMPRESS=${LATEST_DECOMPRESSED_FILE}
FILE_ROOT_DIR_TO_DECOMPRESS=${LATEST_COMPRESSED_FILE_ROOT_DIR}

COMPRESSED_FILE_DIR=${COMPRESSED_FILE_ROOT_DIR}/$(shell echo ${FILE_TO_COMPRESS} | sed 's/.pdf//g')
COMPRESSED_FILE_NAME=$(shell echo ${FILE_TO_COMPRESS} | sed 's/.pdf/.rar/g')

DECOMPRESSED_FILE_NAME=${FILE_ROOT_DIR_TO_DECOMPRESS}.pdf
DECOMPRESSION_FILE_REGEX=${FILE_ROOT_DIR_TO_DECOMPRESS}/${FILE_ROOT_DIR_TO_DECOMPRESS}.rar*

COMPRESSION_LEVEL=5
COMPRESSION_MAX_FILE_SIZE=50M
COMPRESSION_PARAMS=-idq -ep -m${COMPRESSION_LEVEL} -v${COMPRESSION_MAX_FILE_SIZE} ${COMPRESSED_FILE_DIR}/${COMPRESSED_FILE_NAME} ${DECOMPRESSED_FILE_DIR}/${FILE_TO_COMPRESS}

DECOMPRESSION_PARAMS=-idq ${COMPRESSED_FILE_ROOT_DIR}/${DECOMPRESSION_FILE_REGEX}

.PHONY: all
all: build data

.PHONY: build
build:
	@docker-compose build --pull

.PHONY: build-no-cache
build-no-cache:
	@docker-compose build --no-cache

.PHONY: compress-data
compress-data:
	@echo 'Comprimindo arquivo ${FILE_TO_COMPRESS}...'
	@mkdir -p ${COMPRESSED_FILE_DIR}
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} rar a ${COMPRESSION_PARAMS}

.PHONY: data
data: download-data compress-data extract-data process-data

.PHONY: decompress-data
decompress-data:
	@echo 'Descomprimindo arquivo ${DECOMPRESSED_FILE_NAME}...'	
	@if [ -f "${DECOMPRESSED_FILE_DIR}/${DECOMPRESSED_FILE_NAME}" ]; then \
		echo "Arquivo ${DECOMPRESSED_FILE_NAME} já descomprimido, pulando..."; \
	else \
		docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} unrar e ${DECOMPRESSION_PARAMS} \
		&& mv ${DECOMPRESSED_FILE_NAME} ${DECOMPRESSED_FILE_DIR}/${DECOMPRESSED_FILE_NAME}; \
	fi

.PHONY: download-data
download-data:
	@docker-compose run --user=$(shell id -u) --rm ${SERVICE_NAME} python src/download_data.py

.PHONY: extract-data
extract-data: decompress-data
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

.PHONY: shell
shell:
	@docker-compose run --rm ${SERVICE_NAME} bash
