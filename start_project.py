from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import json


def json_serializer(data):
    return json.dumps(data).encode('utf-8')

if __name__ == "__main__":
    #Testcode doesn't work, can't connect to Kafka, maybe bad config in the docker compose
    admin_client = KafkaAdminClient(
        bootstrap_servers="localhost:9092",
        client_id='kafka-service',
        api_version=(0, 9),
    )
    topic_list = []
    topic_list.append(NewTopic(name="my-topic", num_partitions=1, replication_factor=1))
    print('trying to create topic')
    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    print("topic created")
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                             value_serializer=json_serializer)
    producer.send('my-topic', {'test': 'value'})
    print('finished')