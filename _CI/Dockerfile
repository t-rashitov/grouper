FROM python:3.9.7

ENV PYTHONUNBUFFERED 1

COPY app/ /app

WORKDIR /app

RUN pip install --upgrade pip && pip install -r requirements.txt
