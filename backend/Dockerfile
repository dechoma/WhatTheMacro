# ---- Build stage: install dependencies in a slim Python image ----
FROM python:3.12-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ---- Final stage: minimal runtime ----
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src ./src
COPY .env .env

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
