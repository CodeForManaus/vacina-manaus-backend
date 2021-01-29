# vacina-manaus-backend

- [Prerequisites](#prerequisites)
- [Build](#build)
- [Running](#running)
- [Support](#support)
- [Contributing](#contributing)

## Getting started

Run `make all` to build and execute all pipeline

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/ubuntu/) >= 20.10.1
- [Docker-composer](https://docs.docker.com/compose/install/) >= 1.27.4

### Build

To build docker image execute:

```bash
make build
```

To build docker image without cached dependencies:

```bash
make build-no-cache
```

### Running

To extract data from `.pdf` files:

```bash
make extract-data
```

To process the extracted data:

```bash
make process-data
```

To run all pipeline:

```bash
make data
```

## Support

Please [open a issue](https://github.com/CodeForManaus/vacina-manaus-backend/issues/new) for support

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits and [open a pull request](https://github.com/CodeForManaus/vacina-manaus-backend/compare).
