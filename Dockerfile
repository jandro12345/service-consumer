FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#EXPOSE 9002

CMD ["gunicorn", "consumer:app", "--log-level", "DEBUG", "--reload", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:9002"]