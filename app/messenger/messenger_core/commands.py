from datetime import datetime, timezone
import warnings
warnings.simplefilter("ignore", UserWarning)

from faust.cli import option

from ..app import app
from .agents import persist_block_words
from .models import BlockWordMessage
from .tables import block_words_table


@app.command()
async def list_block_words(self):
    """
    Shows the state of the blocked words table
    """

    words = ['миска', 'миска2', 'муха', ]
    for word in words:
        block = block_words_table.get(word, None)
        print(f'{word}: {block}')

    words = block_words_table.keys()
    for word in words:
        block = block_words_table.get(word, None)
        print(f'{word}: {block}')
    return None


@app.command(
    option('--word',
           type=str, default=None,
           help='Word to block|unblock.'),
    option('--block',
           type=bool, default=True,
           help='Block (True) or unblock (False) word.'),
)
async def block_word(self, word: str, block: bool = True):
    """Send well-formed word block message to the corresponding agent"""

    # ОНО по факту отправляет сообщение в топик,
    # если смотреть в UI где что появилось

    message: BlockWordMessage = BlockWordMessage(
        word=word,
        block=block,
        timestamp=datetime.now(tz=timezone.utc),
    )
    # self.say('sending BlockWordMessage')
    print('sending BlockWordMessage')
    # self.say(await persist_block_words.ask(message))
    print(await persist_block_words.ask(message))

    return None

    # TODO: а вот тут оно не выходит из приложения, а мне казалось
    # суть команды в том, чтобы отработать и выйти, а оно висит
    # и кидает на консоль по кругу сообщение:
    # [2025-10-12 13:46:29,185] [335] [WARNING] [^-Consumer]: wait_empty:
    # Waiting for tasks [(1, <ConsumerMessage:
    # TopicPartition(topic='f-reply-4fef7611-223b-44a1-b32a-d3423062ae5a', partition=0) offset=0>)]
    # Это при том, что я на консоли вижу ответ от self.say(await persist_block_words.ask(message)).
