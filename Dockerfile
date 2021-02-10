FROM python:3.8.7-slim

RUN apt-get update && apt-get install -y \
    automake \
    make \
    gcc \
    g++ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app