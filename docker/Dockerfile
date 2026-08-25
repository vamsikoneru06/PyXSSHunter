# ========================
# Builder Stage
# ========================
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# ========================
# Runtime Stage
# ========================
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright-browsers

RUN mkdir -p /app/reports && chown -R appuser:appuser /app

COPY --from=builder /app /app

RUN pip install --no-cache-dir -r requirements.txt

# Playwright needs its own browser binary plus OS-level libs (--with-deps installs both);
# must run as root, before switching to appuser below.
RUN python -m playwright install --with-deps chromium

RUN chown -R appuser:appuser /app

USER appuser

VOLUME ["/app/reports"]

ENTRYPOINT ["python", "-m", "pyxsshunter"]
CMD []