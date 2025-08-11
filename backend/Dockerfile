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

ENV PYTHONPATH=/app/src

# Create and use an unprivileged user; do not bake secrets into the image
RUN useradd -m -u 10001 appuser && \
    chown -R appuser:appuser /app

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
