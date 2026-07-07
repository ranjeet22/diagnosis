FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim as runner

WORKDIR /workspace

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Expose default API port
EXPOSE 8000

# Copy application files
COPY app /workspace/app
COPY README.md /workspace/README.md

# Environment settings
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
