import warnings
warnings.simplefilter("ignore", UserWarning)

import faust
from yarl import URL

from .global_settings import app_global_settings
from ..app import app
from .utils import KafkaAdm


@app.on_after_configured.connect
def after_configuration(signal_sender_app, **kwargs):
    """
    Создаём, при отсутствии, необходимые топики
    синхронно через confluent_kafka.admin.

    Called after messenger is fully configured and ready for use.
    Takes only sender as argument, which is the messenger that was configured:
    This is a synchronous signal (do not use async def).
    """
    # этот сигнал, похоже, вовсе не поднимается
    # bootstrap_servers извлечём из пославшего сигнал приложения
    sender_app_settings: faust.Settings = signal_sender_app.conf
    app_bootstrap_servers: list[URL] = sender_app_settings.broker
    adm_bootstrap_servers = ",".join(
        str(broker.host) + ':' + str(broker.port)
        for broker in app_bootstrap_servers
    )
    # print(f'adm_bootstrap_servers: {adm_bootstrap_servers}')
    adm = KafkaAdm(title='KafkaAdm', bootstrap_servers=adm_bootstrap_servers,
                   timeouts=5.0)

    # остальное - из глобального конфига
    topics_partitions = app_global_settings.get('topics_partitions', 3)
    # print(f'topics_partitions: {topics_partitions}')
    topics_replicas = app_global_settings.get('topics_replicas', 2)
    # print(f'topics_replicas: {topics_replicas}')

    messages_topic_name = app_global_settings.get(
        'messages_topic_name', 'messages')
    blocked_users_topic_name = app_global_settings.get(
        'blocked_users_topic_name', 'blocked_users')
    filtered_messages_topic_name = app_global_settings.get(
        'filtered_messages_topic_name', 'filtered_messages')
    blocked_words_topic_name = app_global_settings.get(
        'blocked_words_topic_name', 'blocked_words')

    # check_topic создаст топик при его отсутствии
    # (при наличии - НЕ проверяет настройки топика)

    # print(f'going to check topic {messages_topic_name}')
    adm.check_topic(topic=messages_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {messages_topic_name}')

    # print(f'going to check topic {blocked_users_topic_name}')
    adm.check_topic(topic=blocked_users_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {blocked_users_topic_name}')

    # print(f'going to check topic {filtered_messages_topic_name}')
    adm.check_topic(topic=filtered_messages_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {filtered_messages_topic_name}')

    # print(f'going to check topic {blocked_words_topic_name}')
    adm.check_topic(topic=blocked_words_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {blocked_words_topic_name}')


@app.on_worker_init.connect
def on_worker_init(signal_sender_app: faust.App, **kwargs):
    """
    Создаём, при отсутствии, необходимые топики
    синхронно через confluent_kafka.admin.

    Called by the faust worker program (or when using messenger.main())
    to apply worker specific customizations.
    Takes only sender as argument,
    which is the messenger a worker is being started for.
    This is a synchronous signal (do not use async def).
    """

    # bootstrap_servers извлечём из пославшего сигнал приложения
    sender_app_settings: faust.Settings = signal_sender_app.conf
    app_bootstrap_servers: list[URL] = sender_app_settings.broker
    adm_bootstrap_servers = ",".join(
        str(broker.host) + ':' + str(broker.port)
        for broker in app_bootstrap_servers
    )
    # print(f'adm_bootstrap_servers: {adm_bootstrap_servers}')
    adm = KafkaAdm(title='KafkaAdm', bootstrap_servers=adm_bootstrap_servers,
                   timeouts=5.0)

    # остальное - из глобального конфига
    topics_partitions = app_global_settings.get('topics_partitions', 3)
    # print(f'topics_partitions: {topics_partitions}')
    topics_replicas = app_global_settings.get('topics_replicas', 2)
    # print(f'topics_replicas: {topics_replicas}')

    messages_topic_name = app_global_settings.get(
        'messages_topic_name', 'messages')
    blocked_users_topic_name = app_global_settings.get(
        'blocked_users_topic_name', 'blocked_users')
    filtered_messages_topic_name = app_global_settings.get(
        'filtered_messages_topic_name', 'filtered_messages')
    blocked_words_topic_name = app_global_settings.get(
        'blocked_words_topic_name', 'blocked_words')

    # check_topic создаст топик при его отсутствии
    # (при наличии - НЕ проверяет настройки топика)

    # print(f'going to check topic {messages_topic_name}')
    adm.check_topic(topic=messages_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {messages_topic_name}')

    # print(f'going to check topic {blocked_users_topic_name}')
    adm.check_topic(topic=blocked_users_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {blocked_users_topic_name}')

    # print(f'going to check topic {filtered_messages_topic_name}')
    adm.check_topic(topic=filtered_messages_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {filtered_messages_topic_name}')

    # print(f'going to check topic {blocked_words_topic_name}')
    adm.check_topic(topic=blocked_words_topic_name,
                    partitions=topics_partitions, replicas=topics_replicas)
    # print(f'checked topic {blocked_words_topic_name}')

    # time.sleep(1)
