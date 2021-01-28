FROM python:3.8.7-slim

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && \
    apt-get install -y make automake gcc g++

RUN pip install -r requirements.txt

COPY . /app
