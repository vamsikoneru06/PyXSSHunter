# ========================
# Builder Stage
# ========================
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# ========================
# Runtime Stage
# ========================
FROM python:3.12-slim

# Minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security best practice)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Create reports directory with proper permissions
RUN mkdir -p /app/reports && chown -R appuser:appuser /app

# Copy installed packages and source from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/pyxsshunter /app/pyxsshunter

# Labels for GitHub and security tools
LABEL org.opencontainers.image.title="PyXSSHunter"
LABEL org.opencontainers.image.description="Stealthy XSS Vulnerability Scanner"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.source="https://github.com/yourusername/PyXSSHunter"

USER appuser

VOLUME ["/app/reports"]

# Better ENTRYPOINT for Typer CLI
ENTRYPOINT ["python", "-m", "pyxsshunter"]

# Default command
CMD ["--help"]