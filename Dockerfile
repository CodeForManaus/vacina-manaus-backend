FROM python:3.8.7-slim

RUN echo "deb http://http.us.debian.org/debian jessie non-free" >> /etc/apt/sources.list

RUN apt-get -yq update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y \
            automake \
            make \
            gcc \
            g++ \
            rar \
            unrar \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /vacina-manaus-backend

COPY . .

RUN pip install -r requirements.txt
