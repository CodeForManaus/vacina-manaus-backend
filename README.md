# vacina-manaus-backend 💉

- [Sobre o projeto](#sobre-o-projeto)
- [Começando](#começando)
  - [Pré-requisitos](#pré-requisitos)
  - [Construindo o projeto](#construindo-o-projeto)
  - [Executando](#running)
- [Como contribuir](#como-contribuir)
- [Licença](#licença)

## Sobre o projeto

Este projeto tem como finalidade extrair os dados disponibilizados pela Prefeitura de Manaus sobre a vacinação na cidade e fornecer os dados para o site vacinamanaus.com

## Começando

Rode `make all` para construir a imagem e rodar todo o pipeline

### Pré-requisitos

- [Docker](https://docs.docker.com/engine/install/ubuntu/) >= 20.10.1
- [Docker Compose](https://docs.docker.com/compose/install/) >= 1.27.4

### Construindo o projeto

Para construir a imagem docker:

```bash
make build
```

Para construir a imagem docker sem dependências armazenadas no cache:

```bash
make build-no-cache
```

### Executando

Para baixar o último arquivo publicado pela prefeitura:

```bash
make download-data
```

Para extrair os dados dos arquivos `.pdf`:

```bash
make extract-data
```

Para processar o arquivo de dados extraídos:

```bash
make process-data
```

Para rodar todo o pipeline de dados:

```bash
make data
```

## Como contribuir

- Abrindo [uma issue](https://github.com/CodeForManaus/vacina-manaus-backend/issues/new) reportando um bug ou sugerindo uma melhoria.
- Por favor contribua usando o [Github Flow](https://guides.github.com/introduction/flow/). Cria uma branch, adicione os commits e [abra uma pull request](https://github.com/CodeForManaus/vacina-manaus-backend/compare).

## Licença

Veja a [LICENÇA](https://github.com/CodeForManaus/vacina-manaus-backend/blob/master/LICENSE.md)
