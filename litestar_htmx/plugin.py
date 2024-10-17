"""Plugin for creating and retrieving flash messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

from litestar_htmx.request import HTMXRequest

if TYPE_CHECKING:
    from litestar.config.app import AppConfig
    from litestar.template import TemplateConfig


@dataclass
class HtmxConfig:
    """Configuration for Flash messages."""

    template_config: TemplateConfig


class HtmxPlugin(InitPluginProtocol):
    """Flash messages Plugin."""

    def __init__(self, config: HtmxConfig):
        """Initialize the plugin.

        Args:
            config: Configuration for flash messages, including the template engine instance.
        """
        self.config = config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Register the message callable on the template engine instance.

        Args:
            app_config: The application configuration.

        Returns:
            The application configuration with the message callable registered.
        """
        app_config.request_class = HTMXRequest
        app_config.signature_types = [HTMXRequest]
        return app_config
