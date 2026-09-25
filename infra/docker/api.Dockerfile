FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services ./services
COPY data ./data
COPY tests ./tests
RUN pip install --no-cache-dir -e ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "services.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
