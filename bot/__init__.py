from pathlib import Path

from aiologger.formatters.json import ExtendedJsonFormatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel
from aiologger.loggers.json import JsonLogger


# Configure logging
Path("logs").mkdir(parents=True, exist_ok=True)
file_handler = AsyncFileHandler(filename="logs/log.json")
file_handler.formatter = ExtendedJsonFormatter()

logger = JsonLogger.with_default_handlers(
    level=LogLevel.INFO,
    serializer_kwargs={
        "ensure_ascii": False,
        "indent": 2,
    },
)

logger.add_handler(file_handler)
