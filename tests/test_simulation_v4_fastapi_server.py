import pytest


pytest.importorskip("fastapi")

from carpet_bombing.simulations.simulation_v4.servers.fastapi.app import (
    COMMAND_HISTORY,
    Command,
    app,
    health,
    receive_command,
    status,
)


def test_api_declares_expected_routes():
    routes = {route.path for route in app.routes}

    assert "/" in routes
    assert "/health" in routes
    assert "/status" in routes
    assert "/command" in routes


def test_health_endpoint_reports_running_api():
    payload = health()

    assert payload["status"] == "ok"
    assert isinstance(payload["uptime_seconds"], float)
    assert payload["uptime_seconds"] >= 0


def test_command_endpoint_stores_received_command():
    COMMAND_HISTORY.clear()

    payload = receive_command(Command(command="probe", target="10.0.0.14"))

    assert payload["accepted"] is True
    assert payload["received"]["command"] == "probe"
    assert payload["received"]["target"] == "10.0.0.14"
    assert len(COMMAND_HISTORY) == 1

    assert status()["commands_received"] == 1
