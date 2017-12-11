FROM python:3

WORKDIR /workspace
RUN pip install sphinx sphinx-rtd-theme pytest pytest-cov
COPY . .
RUN pip install -e core -e google
