# consumer-service
```
gunicorn consumer:app --log-level DEBUG --reload --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:9002
```

# RabbitMQ
```
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```