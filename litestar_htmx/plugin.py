"""Plugin for creating and retrieving flash messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

from litestar_htmx.request import HTMXRequest
from litestar_htmx.response import (
    ClientRedirect,
    ClientRefresh,
    HTMXTemplate,
    HXLocation,
    HXStopPolling,
    PushUrl,
    ReplaceUrl,
    Reswap,
    Retarget,
    TriggerEvent,
)

if TYPE_CHECKING:
    from litestar.config.app import AppConfig


class HTMXPlugin(InitPluginProtocol):
    """Flash messages Plugin."""

    def __init__(self):
        """Initialize the plugin."""

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Register the message callable on the template engine instance.

        Args:
            app_config: The application configuration.

        Returns:
            The application configuration with the message callable registered.
        """
        app_config.request_class = HTMXRequest
        app_config.signature_types = [
            HTMXRequest,
            ClientRedirect,
            ClientRefresh,
            HTMXTemplate,
            HXLocation,
            HXStopPolling,
            PushUrl,
            ReplaceUrl,
            Reswap,
            Retarget,
            TriggerEvent,
        ]
        return app_config
