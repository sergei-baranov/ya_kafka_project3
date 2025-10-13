from datetime import datetime
import warnings
warnings.simplefilter("ignore", UserWarning)

import faust


class User2UserMessage(faust.Record):
    user_id: str
    recipient_id: str
    timestamp: datetime
    message: str


class BlockUserMessage(faust.Record):
    recipient_id: str
    donor_id: str
    timestamp: datetime
    block: bool


class BlockWordMessage(faust.Record):
    word: str
    timestamp: datetime
    block: bool
