import pytest
from litestar.config.app import AppConfig

from litestar_htmx import HTMXConfig, HTMXPlugin, HTMXRequest

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "set_request_class_globally",
    (True, False),
)
def test_request_class(set_request_class_globally: bool) -> None:
    config = HTMXConfig(set_request_class_globally=set_request_class_globally)
    plugin = HTMXPlugin(config=config)
    app_config = plugin.on_app_init(AppConfig())
    if set_request_class_globally:
        assert app_config.request_class == HTMXRequest
    else:
        assert app_config.request_class is None


class CustomHTMXRequest(HTMXRequest):
    """Extra functionality."""


def test_request_class_no_override() -> None:
    plugin = HTMXPlugin()
    app_config = plugin.on_app_init(AppConfig(request_class=CustomHTMXRequest))
    assert app_config.request_class == CustomHTMXRequest
