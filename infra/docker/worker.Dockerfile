FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services ./services
COPY data ./data
RUN pip install --no-cache-dir -e .
CMD ["python", "-m", "services.cv_worker.pipeline"]
