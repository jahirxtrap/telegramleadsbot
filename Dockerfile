FROM python:3.11-slim

WORKDIR /app

# Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Application code
COPY . .

EXPOSE 8000

CMD ["python", "run.py", "--production"]
