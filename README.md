 - Detecção de fraudes em transações financeiras utilizando Apache Kafka e Apache Cassandra

  -> Visão Geral: Esse projeto tem como objetivo detectar transações fraudulentas em tempo real usando Apache Kafka e Cassandra. 
     As transações são geradas por um producer e são consumidas por um consumer que se aplica as regras de fraude, e são armazenadas no Cassandra para análise posterior.

  -> Estrutura do Projeto

            Kafka/
        │── consumer/
        │   ├── consumer.py
        │   ├── Dockerfile
        │   ├── requirements.txt
        │
        │── producer/
        │   ├── producer.py
        │   ├── transaction_generator.py
        │   ├── Dockerfile
        │   ├── requirements.txt
        │
        │── docker-compose.yml
        │── README.md
        

  -> Tecnologias Utilizadas
   
    * Apache Kafka: Mensageria para transmissão de transação.
    * Python: Linguagem utilizada para desenvolver o Producer e Consumer.
    * Docker & Docker Compose: Facilita a execução dos serviços.
    * Apache Cassandra.

  -> Como funciona

   1 - O producer gera transações fictícias e as envia para o Kafka
   2 - O consumer recebe as transações do Kafka e aplica as regras para detectar fraudes.
        * Alta frequência: Duas transações com valores diferentes em menos de 5 minutos.
        * Alto valor: Uma transação que excede o dobro do maior valor anterior.
        * Outro país: Uma transação realizada em um país diferente em menos de 2 horas.


  -> Como executar

    1 - Subir os conteiners com Docker Compose

      *  docker-compose build

      *  docker-compose up

      - Isso iniciará os seguinte serviços.

        * Kafka
        * Zookeeper
        * Cassandra
        * Producer
        * Consumer


    2 - Verificação do conteiners

      * docker posterior

    3 - Acompanhamento de de logs do Consumer

      * docker logs -f consumer

  -> Consultando dados no Cassandra

      * docker exec -it cassandra cqlsh;

      - consulta keyspace:

      * use fraud_detection;

      - consulta de fraudes

      select count(*) from fraud_alerts (Obs: no Cassandra utilizar count diretamente, não é uma opção correta em se usar devido ao número de transações armazenada, utilizar where com a primary key(partition key))

      select * from fraud_alerts limit 10; - ()
