import os
import json
import time
from kafka import KafkaConsumer, KafkaProducer
from cassandra.cluster import Cluster

cassandra_host = os.environ.get('CASSANDRA_HOST', 'cassandra')
kafka_broker = os.environ.get('KAFKA_BROKER', 'kafka:9092')

print("Aguardando conexão com Cassandra...")
while True:
    try:
        cluster = Cluster([cassandra_host])
        session = cluster.connect()
        print("Conectado ao Cassandra!")
        break
    except Exception as e:
        print(f"Erro ao conectar ao Cassandra: {e}")
        time.sleep(5)

try:
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS fraud_detection
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """)
    session.set_keyspace('fraud_detection')

    session.execute("""
        CREATE TABLE IF NOT EXISTS fraud_alerts (
            user_id int,
            transaction_id int,
            fraud_type text,
            timestamp int,
            PRIMARY KEY (user_id, transaction_id)
        )
    """)
    print("Keyspace e tabela configurados!")
except Exception as e:
    print(f"Erro ao configurar Cassandra: {e}")


print("Aguardando conexão com Kafka...")
while True:
    try:
        consumer = KafkaConsumer(
            'transacoes',
            bootstrap_servers=kafka_broker,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print("Conectado ao Kafka!")
        break
    except Exception as e:
        print(f"Erro ao conectar ao Kafka: {e}")
        time.sleep(5)

producer = KafkaProducer(
    bootstrap_servers=kafka_broker,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Histórico do usuário para detecção de fraudes
user_history = {}

def detect_fraud(tx):
    frauds = []
    user_id = tx['user_id']
    ts = tx['timestamp']
    value = tx['value']
    country = tx['country']

    if user_id in user_history:
        last_tx = user_history[user_id]['last_tx']
        if abs(ts - last_tx['timestamp']) < 300 and value != last_tx['value']:
            frauds.append('Alta Frequência')
        if value > 2 * user_history[user_id]['max_value']:
            frauds.append('Alto Valor')
        if country != last_tx['country'] and abs(ts - last_tx['timestamp']) < 7200:
            frauds.append('Outro País')

    user_history[user_id] = {
        'last_tx': tx,
        'max_value': max(user_history.get(user_id, {}).get('max_value', 0), value)
    }

    return frauds

print("Consumidor Kafka iniciado!")
try:
    for message in consumer:
        tx = message.value
        frauds = detect_fraud(tx)
        if frauds:
            alert = {
                'user_id': tx['user_id'],
                'transaction_id': tx['transaction_id'],
                'fraud_types': frauds,
                'timestamp': tx['timestamp']
            }
            producer.send('fraudes_detectadas', value=alert)
            print(f"Fraude detectada: {alert}")
            
            for fraud in frauds:
                session.execute(
                    "INSERT INTO fraud_alerts (user_id, transaction_id, fraud_type, timestamp) VALUES (%s, %s, %s, %s)",
                    (tx['user_id'], tx['transaction_id'], fraud, tx['timestamp'])
                )
except KeyboardInterrupt:
    print("\nInterrompido pelo usuário.")
finally:
    print("Finalizando consumidor...")
    consumer.close()
    producer.close()
    cluster.shutdown()
