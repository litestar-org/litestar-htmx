from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest
from litestar import Response, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.exceptions import ImproperlyConfiguredException
from litestar.template.config import TemplateConfig
from litestar.testing import create_test_client

from litestar_htmx import TriggerEventNameType
from litestar_htmx.response import HTMXTemplate, TriggerEvent
from litestar_htmx.types import EventAfterType


@pytest.mark.parametrize(
    "after, header",
    (
        ("receive", "HX-Trigger"),
        ("settle", "HX-Trigger-After-Settle"),
        ("swap", "HX-Trigger-After-Swap"),
    ),
)
@pytest.mark.parametrize(
    "events, params, expected",
    (
        (("event1", "event2"), None, {"event1": {}, "event2": {}}),
        (MappingProxyType({"event1": "Message", "event2": {}}), None, {"event1": "Message", "event2": {}}),
        (
            ["update_user_roles", "update_role_permissions"],
            None,
            {"update_user_roles": {}, "update_role_permissions": {}},
        ),
        (["event1", "event2"], {"alert": "Updated"}, {"event1": {"alert": "Updated"}, "event2": {"alert": "Updated"}}),
        (
            {"event1": "A message", "event2": "Another message"},
            None,
            {"event1": "A message", "event2": "Another message"},
        ),
        (
            {"event1": {"target": "#other", "count": 2}, "event2": {}},
            None,
            {"event1": {"target": "#other", "count": 2}, "event2": {}},
        ),
        (
            {"event1": False, "event2": None, "event3": 0, "event4": ""},
            None,
            {"event1": False, "event2": None, "event3": 0, "event4": ""},
        ),
    ),
)
@pytest.mark.parametrize("use_template", (False, True))
def test_multiple_trigger_events(
    after: EventAfterType,
    header: str,
    events: TriggerEventNameType,
    params: dict[str, Any] | None,
    expected: dict[str, Any],
    use_template: bool,
    tmp_path: Path,
) -> None:
    (tmp_path / "partial.html").write_text("Success!")

    @get("/")
    def handler() -> Response[Any]:
        if use_template:
            return HTMXTemplate(template_name="partial.html", trigger_event=events, params=params, after=after)
        return TriggerEvent(content="Success!", name=events, params=params, after=after)

    with create_test_client(
        route_handlers=[handler],
        template_config=TemplateConfig(directory=tmp_path, engine=JinjaTemplateEngine),
    ) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Success!"
        assert json.loads(response.headers[header]) == expected
        assert sum(name.startswith("hx-trigger") for name in response.headers) == 1


@pytest.mark.parametrize("use_template", (False, True))
@pytest.mark.parametrize("params", ({}, {"alert": "Ambiguous"}))
@pytest.mark.parametrize("events", ({}, {"event1": {}}))
def test_event_dictionary_rejects_separate_params(
    use_template: bool, params: dict[str, Any], events: dict[str, Any]
) -> None:
    with pytest.raises(ImproperlyConfiguredException, match="params"):
        if use_template:
            HTMXTemplate(template_name="partial.html", trigger_event=events, params=params, after="receive")
        else:
            TriggerEvent(content="Success!", name=events, params=params, after="receive")


@pytest.mark.parametrize("events", (["event1", "event2"], {"event1": {}, "event2": {}}))
@pytest.mark.parametrize("use_template", (False, True))
def test_multiple_trigger_events_require_valid_after(events: TriggerEventNameType, use_template: bool) -> None:
    with pytest.raises(ImproperlyConfiguredException, match="after"):
        if use_template:
            HTMXTemplate(template_name="partial.html", trigger_event=events)
        else:
            TriggerEvent(content="Success!", name=events, after=None)


@pytest.mark.parametrize("events", ([], {}))
@pytest.mark.parametrize("use_template", (False, True))
def test_empty_trigger_events(events: TriggerEventNameType, use_template: bool) -> None:
    response: Response[Any]
    if use_template:
        response = HTMXTemplate(template_name="partial.html", trigger_event=events, after="receive")
    else:
        response = TriggerEvent(content="Success!", name=events, after="receive")
    assert response.headers["HX-Trigger"] == "{}"


def test_template_empty_event_name_preserves_no_trigger() -> None:
    response = HTMXTemplate(template_name="partial.html", trigger_event="")
    assert "HX-Trigger" not in response.headers
