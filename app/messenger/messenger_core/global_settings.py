app_global_settings = {
    'messages_topic_name': 'messages',
    'blocked_users_topic_name': 'blocked_users',
    'filtered_messages_topic_name': 'filtered_messages',
    'blocked_words_topic_name': 'blocked_words',
    'topics_partitions': 3,
    'topics_replicas': 2,
    'bootstrap_servers': (
        'kafka://kafka-0:9092',
        'kafka://kafka-1:9092',
        'kafka://kafka-2:9092',
    ),
}
