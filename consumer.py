"""
Consumer service
"""
import json
from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
from psycopg2 import connect
from threading import Thread
from contextlib import asynccontextmanager
from tool import connect_to_rabbitmq, logger, DSN



def callback(ch, method, properties, body):
    json_data = json.loads(body)
    logger.info(f"Received message: {json_data}")
    
    with connect(dsn=DSN, cursor_factory=RealDictCursor) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                update
                    tbl_payment_method
                set
                    updated_at=NOW(),
                    validate_fund= validate_fund - %(amount)s
                where
                    payment_method_id = %(payment_method_id)s
                returning payment_method_id
                """, {
                    "payment_method_id": json_data["payment_method_id"],
                    "amount": json_data["amount"],
                }
            )
            
            cur.execute(
                """
                Insert into tbl_transaction (
                    amount,
                    payment_method_id
                ) values (
                    %(amount)s,
                    %(payment_method_id)s
                )
                returning transaction_id
                """, {
                    "amount": json_data["amount"],
                    "payment_method_id": json_data["payment_method_id"],
                }
            )
            data_transaction = cur.fetchone()
    logger.info(f"Transaction: {data_transaction["transaction_id"]}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_messages():
    channel = connect_to_rabbitmq()
    channel.queue_declare(queue="payment_queue", durable=True)
    
    channel.basic_consume(queue="payment_queue", on_message_callback=callback)
    logger.info("Waiting for messages.")
    channel.start_consuming()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    consumer_thread = Thread(target=consume_messages)
    consumer_thread.daemon = True
    consumer_thread.start()
    yield
    logger.info("Shutting down application...")

app = FastAPI(lifespan=lifespan)

