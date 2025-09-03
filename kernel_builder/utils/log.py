import logging
from logging import FileHandler, Filter, Handler, Logger, LogRecord
from pathlib import Path
from typing import override

from rich.console import Console
from rich.logging import RichHandler

logger: Logger = logging.getLogger("gki_builder")
console: Console = Console(color_system="auto")


class ShFilter(Filter):
    @override
    def filter(self, record: LogRecord):
        if record.name.startswith("sh"):
            return False
        return True


def configure_log(
    *, level: int = logging.INFO, logfile: str | Path | None = None
) -> None:
    """
    Initialize logging if NOT configured.

    :param level: Logging level, default is INFO.
    :return: None
    """

    if logger.handlers:
        return

    filter: ShFilter = ShFilter()

    rich_handlers: RichHandler = RichHandler(
        console=console,
        omit_repeated_times=False,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
    )
    rich_handlers.addFilter(filter)

    handlers: list[Handler] = [rich_handlers]

    if logfile:
        file_handler: FileHandler = logging.FileHandler(logfile)
        file_handler.addFilter(filter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )


def log(message: str, level: str = "info") -> None:
    """
    Simple wrapper for logging.

    :param message: Message to log.
    :param level: Log level, default is info.
    :return: None
    """
    match level.lower():
        case "info":
            logger.info(message)
        case "warn" | "warning":
            logger.warning(message)
        case "error":
            logger.error(message)
        case _:
            logger.info(message)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
