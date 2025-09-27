import pytest
import json
from pathlib import Path

HERE = Path(__file__).parent


def payloads() -> dict[str, dict]:
    loaded_payloads = {}
    for payload in (HERE / "payloads").glob("payload*.json"):
        idx = payload.stem.replace("payload", "")
        loaded_payloads[idx] = json.loads(payload.read_text())
    return loaded_payloads


def responses() -> dict[str, dict]:
    loaded_responses = {}
    for response in (HERE / "responses").glob("response*.json"):
        idx = response.stem.replace("response", "")
        loaded_responses[idx] = json.loads(response.read_text())
    return loaded_responses


def assembled_payload_responses() -> list[tuple[dict, ...]]:
    assembled = []
    loaded_responses = responses()
    for k, v in payloads().items():
        assembled.append((v, loaded_responses.get(k)))
    return assembled


@pytest.mark.parametrize("payload_response", assembled_payload_responses())
def test_payloads(payload_response, client):
    payload, expected_response = payload_response
    if expected_response is None:
        pytest.fail(f"No response for payload")

    response = client.post("/productionplan", json=payload)
    assert response.status_code == 200, expected_response.text
    assert response.json() == expected_response
