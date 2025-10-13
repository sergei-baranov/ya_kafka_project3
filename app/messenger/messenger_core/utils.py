from confluent_kafka import KafkaException
from confluent_kafka.admin import (AdminClient, ClusterMetadata, NewTopic,
                                   TopicMetadata)


class KafkaAdm:
    def __init__(self, title: str, bootstrap_servers: str, timeouts: float):
        self.title = title
        self.bootstrap_servers = bootstrap_servers
        self.timeouts = timeouts

    def check_topic(self, topic: str, partitions: int, replicas: int):
        client = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        try:
            metadata: ClusterMetadata = client.list_topics(
                topic=topic, timeout=self.timeouts)
            topics_meta: dict[str, TopicMetadata] = metadata.topics
            topic_meta: TopicMetadata = topics_meta.get(topic)
            if topic_meta is None:
                new_topic = NewTopic(
                    topic,
                    num_partitions=partitions,
                    replication_factor=replicas,
                )
                client.create_topics([new_topic])
        except KafkaException as e:
            print(f'[{self.title}] check_topic: KafkaException')
            print(e)
            raise e
