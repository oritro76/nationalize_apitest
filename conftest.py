from pathlib import Path
from loguru import logger
import pytest
from _pytest.logging import caplog as _caplog
import logging
import os


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(
        PropogateHandler(), format="{message} {extra}", level="TRACE"
    )
    yield _caplog
    logger.remove(handler_id)


@pytest.fixture(autouse=True)
def write_logs(request):
    # put logs in tests/logs
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    log_path = Path(os.path.join(ROOT_DIR, "logs", "tests"))

    # tidy logs in subdirectories based on test module and class names
    module = request.module
    class_ = request.cls
    name = request.node.name + ".log"

    if module:
        log_path /= module.__name__.replace("tests.", "")
    if class_:
        log_path /= class_.__name__

    log_path.mkdir(parents=True, exist_ok=True)

    # append last part of the name
    log_path /= name

    # enable the logger
    logger.remove()
    logger.configure(handlers=[{"sink": log_path, "level": "TRACE", "mode": "w"}])
    logger.enable("my_package")
