from ..app import app

block_words_table = app.Table('block_words_table', default=bool)
block_users_table = app.Table('block_users_table', default=dict[str, bool])
