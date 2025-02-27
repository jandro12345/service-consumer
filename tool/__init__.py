"""
Tools
"""
import json
import logging
from os import getenv
from typing import Annotated, Any
from dotenv import load_dotenv
from fastapi import HTTPException, Header
import jwt
import pika

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

load_dotenv()


DSN = f"""
    user={getenv("PG_USER", "0")}
    password={getenv("PG_PASS", "0")}
    host={getenv("PG_HOST", "0")}
    port={getenv("PG_PORT", "0")}
    dbname={getenv("PG_DB", "0")}
    """



async def verification_token(Token: Annotated[Any, Header()]):
    """
    verification token
    """
    try:
        token_decode = jwt.decode(Token, getenv("TOKEN"), algorithms=["HS256"])
        if not token_decode.get("authorized-transaction"):
            raise HTTPException(status_code=404, detail="Not Found")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=400, detail="Invalid Token") from exc
    return Token


def connect_to_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672))
    channel = connection.channel()
    return channel


def send_message(channel, queue_name, message):
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )