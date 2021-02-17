FROM python:3.9

RUN apt-get -yq update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y \
            build-essential \
            pdftk \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /vacina-manaus-backend

COPY . .

RUN pip install -r requirements.txt
