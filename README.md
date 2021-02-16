# vacina-manaus-backend 💉

- [Sobre o projeto](#sobre-o-projeto)
  - [Organização dos diretórios](#organização-dos-diretórios)
- [Começando](#começando)
  - [Pré-requisitos](#pré-requisitos)
  - [Construindo o projeto](#construindo-o-projeto)
  - [Executando](#running)
- [Como contribuir](#como-contribuir)
- [Licença](#licença)

## Sobre o projeto

Este projeto tem como finalidade extrair os dados disponibilizados pela Prefeitura de Manaus sobre a vacinação na cidade e fornecer os dados para o site vacinamanaus.com

### Organização dos diretórios

Este projeto está organizado nos seguintes diretórios:
- `src`: Diretório contendo todos os códigos em Python que são executados durante o processo de tratamento e análise dos dados.
- `data/raw`: Diretório contendo todos os relatórios em arquivos PDF disponibilizado pela secretaria de saúde e coletados através de um *web crawler*.
- `data/cleaned`: Diretório contendo arquivos JSON que foram extraídos dos relatórios e tiveram os campos limpos e normalizados.
- `data/analyzed`: Diretório contendo arquivos CSV que contém analises geradas a partir dos dados limpos. Estes arquivos alimentarão as visualizações do front-end.

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
