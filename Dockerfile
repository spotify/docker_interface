FROM python:3

RUN apt-get update \
    && apt-get install zip -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN pip install -e .
