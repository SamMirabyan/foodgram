FROM python:3.8.10-slim

WORKDIR /app
COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .