import pytest
import logging
import os
import responses
from functools import partial
from pathlib import Path
from loguru import logger
from responses import RequestsMock
from _pytest.logging import caplog as _caplog

from settings import url
from mocks.mocks import generate_nationalize_api_mock_responses


def pytest_addoption(parser):
    parser.addoption("--use-real-api", action="store_true", help="Use real API instead of mock responses")

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

@pytest.fixture(scope="function")
def mock_responses(request):
  """
  Creates a responses object with mock responses (if enabled), registers it as a fixture for each test.
  """
  use_real_api = None
  try:
    use_real_api = request.config.getoption("--use-real-api")
  except ValueError:
    pass

  if not use_real_api:  
    with RequestsMock() as m:
      m.add_callback(
          method=responses.GET,
          url=url,  
          callback=partial(
              generate_nationalize_api_mock_responses,
              test_name=request.node.name
          ),
          content_type="application/json",
      )
      yield m
  else:  
    yield None  


