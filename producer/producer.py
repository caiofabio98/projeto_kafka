import time
from kafka import KafkaProducer
import json
import logging
import os
from dataclasses import asdict
from transaction_generator import TransactionGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')

# Tentativa de conexão com o Kafka (com timeout)
while True:
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        logging.info("Conectado ao Kafka com sucesso!")
        break
    except Exception as e:
        logging.error(f"Kafka não disponível ainda: {e}")
        time.sleep(5)  # Espera 5 segundos antes de tentar novamente

transaction_generator = TransactionGenerator(trans_per_sec=10)

try:
    for tx in transaction_generator.generate_transactions():
        tx_dict = asdict(tx)

        try:
            producer.send('transacoes', value=tx_dict)
            logging.info(f"Transação enviada: {tx_dict}")
        except Exception as e:
            logging.error(f"Erro ao enviar transação: {e}")

except KeyboardInterrupt:
    logging.info("Interrompido pelo usuário.")

finally:
    logging.info("Finalizando Producer...")
    producer.flush()
    producer.close()
