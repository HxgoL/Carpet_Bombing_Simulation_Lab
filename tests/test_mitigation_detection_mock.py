import json
from pathlib import Path

from carpet_bombing.mitigation import MitigationController, MitigationEvent
from carpet_bombing.mitigation.backends.dry_run import DryRunBackend
from carpet_bombing.mitigation.models import MitigationActionType


MOCK_ALERTS_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "carpet_bombing"
    / "mitigation"
    / "mock_detection_alerts.json"
)

REQUIRED_ALERT_FIELDS = {
    "alert_id",
    "window_start",
    "window_end",
    "label",
    "severity",
    "confidence",
    "src_ip",
    "suspect_sources",
    "dst_prefix",
    "protocol",
    "packet_count",
    "byte_count",
    "packets_per_second",
    "unique_dst_count",
    "recommended_action",
}


def load_mock_alerts() -> dict:
    with MOCK_ALERTS_PATH.open(encoding="utf-8") as mock_file:
        return json.load(mock_file)


def alert_to_mitigation_event(alert: dict) -> MitigationEvent:
    return MitigationEvent(
        label=alert["label"],
        target_prefix=alert["dst_prefix"],
        packets_per_second=alert["packets_per_second"],
        unique_dst_count=alert["unique_dst_count"],
        confidence=alert["confidence"],
        metadata=alert,
    )


def test_detection_mock_file_respects_expected_contract():
    payload = load_mock_alerts()

    assert payload["schema_version"] == "1.0"
    assert payload["source"] == "detection"
    assert payload["alerts"]

    for alert in payload["alerts"]:
        assert REQUIRED_ALERT_FIELDS <= set(alert)
        assert 0.0 <= alert["confidence"] <= 1.0
        assert alert["src_ip"] in alert["suspect_sources"]
        assert all(isinstance(src_ip, str) for src_ip in alert["suspect_sources"])
        assert alert["recommended_action"] in {"monitor", "rate_limit", "block", "redirect"}
        assert alert["severity"] in {"low", "medium", "high", "critical"}


def test_mitigation_can_consume_mock_detection_alerts_in_dry_run():
    payload = load_mock_alerts()
    backend = DryRunBackend()
    controller = MitigationController(backend=backend)

    actions = [
        controller.handle_event(alert_to_mitigation_event(alert))
        for alert in payload["alerts"]
    ]

    attack_action = actions[0]
    normal_action = actions[1]

    assert attack_action is not None
    assert attack_action.action_type == MitigationActionType.DYNAMIC_FILTER
    assert attack_action.target == "10.20.1.0/24"
    assert attack_action.parameters["protocol"] == "udp"
    assert attack_action.parameters["dry_run"] is True
    assert len(backend.applied_actions) == 1

    assert normal_action is None
