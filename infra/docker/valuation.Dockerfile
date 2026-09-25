FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services ./services
COPY data ./data
RUN pip install --no-cache-dir -e .
EXPOSE 8001
CMD ["uvicorn", "services.valuation.app:app", "--host", "0.0.0.0", "--port", "8001"]
