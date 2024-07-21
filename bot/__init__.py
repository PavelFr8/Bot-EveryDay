from aiologger.loggers.json import JsonLogger


# Configure logging
logger = JsonLogger.with_default_handlers(
    level='DEBUG',
    serializer_kwargs={'ensure_ascii': False},
)
