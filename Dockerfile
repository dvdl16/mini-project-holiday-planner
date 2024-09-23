# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install requirements
COPY pyproject.toml /app/
RUN pip install --editable .[dev]

COPY . /app/