import warnings

warnings.simplefilter("ignore", UserWarning)

import faust

from .messenger_core.global_settings import app_global_settings

app = faust.App(
    'simple_messenger_app',
    broker=app_global_settings.get(
        'bootstrap_servers', 'kafka://localhost:9092'),
    store='rocksdb://',
    autodiscover=True,
    origin='messenger',
    # processing_guarantee='exactly_once',
)


def main() -> None:
    app.main()
