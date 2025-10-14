import re
from typing import AsyncIterable

from faust import StreamT
import mode

from ..app import app
from .models import BlockUserMessage, BlockWordMessage, User2UserMessage
from .tables import block_users_table, block_words_table
from .topics import (blocked_users_topic, blocked_words_topic,
                     filtered_messages_topic, messages_topic)


@app.agent(
    messages_topic,
    sink=[filtered_messages_topic],
    supervisor_strategy=mode.CrashingSupervisor,
)
async def filter_messages(messages):
    """
    если отправитель user_id
    не заблокирован получателем recipient_id,
    то yield-им сообщение,
    маскировав в поле message заблокированные слова
    """
    msg: User2UserMessage
    # TODO: schema с определением и key_type, и value_type, в качестве key
    # использовать user_id, тогда поток не надо репартиционировать
    # через group_by
    async for msg in messages.group_by(User2UserMessage.user_id):
        if (
            msg.user_id not in block_users_table
            or msg.recipient_id not in block_users_table[msg.user_id]
        ):
            for word in block_words_table:
                pattern = re.compile(f'\\b{re.escape(word)}\\b', re.I)
                msg.message = re.sub(pattern, '***', msg.message)
            yield msg


@app.agent(
    blocked_words_topic,
    supervisor_strategy=mode.CrashingSupervisor
)
async def persist_block_words(
        messages: StreamT[BlockWordMessage]) -> AsyncIterable[str]:
    """
    поток сообщений-команд о блокировке/разблокировке слов
    агрегирует в таблицу, где ключ - слово,
    значение - bool
    """
    msg: BlockWordMessage
    # TODO: schema с определением и key_type, и value_type, в качестве key
    # использовать word, value_type=ищщдб тогда поток не надо
    # репартиционировать через group_by
    async for msg in messages.group_by(BlockWordMessage.word):
        if msg.block:
            block_words_table[msg.word] = True
        else:
            block_words_table.pop(msg.word, False)
        # тут yield нужен для ответа на ask() извне например
        yield msg.word + ': ' + str(block_words_table.get(msg.word, False))


@app.agent(
    blocked_users_topic,
    supervisor_strategy=mode.CrashingSupervisor
)
async def persist_block_users(messages):
    """
    поток сообщений-команд о блокировке/разблокировке отправителя получателем
    агрегирует в таблицу, где ключ - получатель сообщений,
    значение - словарь с заблокированными отправителями (как ключами словаря)
    """
    msg: BlockUserMessage
    # TODO: schema с определением и key_type, и value_type, в качестве key
    # использовать recipient_id, тогда поток не надо репартиционировать
    # через group_by
    async for msg in messages.group_by(BlockUserMessage.recipient_id):
        blocked_donors: dict[str, bool] = block_users_table[msg.recipient_id]

        if msg.block:
            blocked_donors[msg.donor_id] = True
        else:
            blocked_donors.pop(msg.donor_id, False)

        if blocked_donors:
            block_users_table[msg.recipient_id] = blocked_donors
        else:
            block_users_table.pop(msg.recipient_id, {})
