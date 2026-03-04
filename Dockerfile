FROM ubuntu:latest
LABEL authors="mathis"

ENTRYPOINT ["top", "-b"]

# Do not use this in production environments:
FROM python:3.12-slim

WORKDIR /code

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]