FROM apache/superset:6.1.0

USER root
COPY requirements-local.txt /app/requirements-local.txt
RUN mkdir -p /app/pythonpath && uv pip install --no-cache-dir -r /app/requirements-local.txt
USER superset