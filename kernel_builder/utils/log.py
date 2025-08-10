import logging
import re
from logging import FileHandler, Filter, Handler, Logger, LogRecord
from pathlib import Path
from re import Match, Pattern
from typing import override

from rich.console import Console
from rich.logging import RichHandler

logger: Logger = logging.getLogger("gki_builder")
console: Console = Console(color_system="auto")


class ShFilter(Filter):
    _COMMAND: Pattern[str] = re.compile(r"<Command '(.*?)'(?:, pid (\d+))?>")

    @override
    def filter(self, record: LogRecord):
        if record.name.startswith("sh"):
            msg = record.getMessage()
            if msg.endswith(": process started"):
                msg = msg[: -len(": process started")]

            m: Match[str] | None = self._COMMAND.search(msg)
            if m:
                cmd, _ = m.group(1), m.group(2)
                pretty = f"Running: {cmd}"
                msg = msg.replace(m.group(0), pretty)
            record.msg = msg
            record.args = ()
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
        case "debug":
            logger.debug(message)
        case "info":
            logger.info(message)
        case "warn" | "warning":
            logger.warning(message)
        case "error":
            logger.error(message)
        case "critical":
            logger.critical(message)
        case _:
            logger.warning("Unknown log level %s; defaulting to INFO", level)
            logger.info(message)


if __name__ == "__main__":
    raise SystemExit("This file is meant to be imported, not executed.")
