"""Repairs platform to Restart HA"""

# Adopted from HACS repairs.py

from __future__ import annotations

import logging
from typing import Any

from homeassistant import data_entry_flow
from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import HomeAssistant
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


class RestartRequiredFixFlow(RepairsFlow):
    """Handler for an issue fixing flow."""

    def __init__(self, issue_id: str) -> None:
        self.issue_id = issue_id

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the first step of a fix flow."""

        return await self.async_step_confirm_restart()

    async def async_step_confirm_restart(
        self, user_input: dict[str, str] | None = None
    ) -> data_entry_flow.FlowResult:
        """Handle the confirm step of a fix flow."""
        if user_input is not None:
            _LOGGER.debug(f"[async_step_confirm_restart] user_input: {user_input}")
            await self.hass.services.async_call("homeassistant", "restart")
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="confirm_restart",
            data_schema=vol.Schema({}),
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    *args: Any,
    data: dict[str, str | int | float | None] | None = None,
    **kwargs: Any,
) -> RepairsFlow | None:
    """Create flow."""
    _LOGGER.debug(f"[async_create_fix_flow] issue_id: {issue_id}")
    _LOGGER.debug(f"[async_create_fix_flow] data: {data}")
    if issue_id.startswith("restart_required"):
        return RestartRequiredFixFlow(issue_id)
    return None
