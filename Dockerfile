FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY app/ ./app/

RUN useradd --uid 1000 --create-home --shell /bin/false appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5055

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:5055/healthz', timeout=3)" || exit 1

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:5055", "--workers", "1", "--threads", "4", "--timeout", "60", "main:app"]