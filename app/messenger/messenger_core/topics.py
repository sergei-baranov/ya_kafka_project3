from .global_settings import app_global_settings
from .models import BlockUserMessage, BlockWordMessage, User2UserMessage
from ..app import app


messages_topic_name = app_global_settings.get(
    'messages_topic_name', 'messages')
filtered_messages_topic_name = app_global_settings.get(
    'filtered_messages_topic_name', 'filtered_messages')
blocked_users_topic_name = app_global_settings.get(
    'blocked_users_topic_name', 'blocked_users')
blocked_words_topic_name = app_global_settings.get(
    'blocked_words_topic_name', 'blocked_words')

messages_topic = app.topic(
    messages_topic_name, value_type=User2UserMessage)
filtered_messages_topic = app.topic(
    filtered_messages_topic_name, value_type=User2UserMessage)
blocked_users_topic = app.topic(
    blocked_users_topic_name, value_type=BlockUserMessage)
blocked_words_topic = app.topic(
    blocked_words_topic_name, value_type=BlockWordMessage)
