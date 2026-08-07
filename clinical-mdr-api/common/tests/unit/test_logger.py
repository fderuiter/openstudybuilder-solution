import json
import logging
import pytest
from fastapi import Request
from common.config import settings
from common.logger import log_exception


def create_mock_request(
    method: str = "POST",
    path: str = "/test",
    headers: list = None,
    body_bytes: bytes = b"",
    query_string: bytes = b"",
) -> Request:
    if headers is None:
        headers = []

    # Starlette expects headers as list of (bytes, bytes)
    formatted_headers = []
    for h, v in headers:
        hk = h.encode("utf-8") if isinstance(h, str) else h
        vk = v.encode("utf-8") if isinstance(v, str) else v
        formatted_headers.append((hk, vk))

    scope = {
        "type": "http",
        "method": method,
        "path": f"http://localhost{path}",
        "headers": formatted_headers,
        "query_string": query_string,
    }

    async def receive():
        return {
            "type": "http.request",
            "body": body_bytes,
            "more_body": False,
        }

    return Request(scope, receive=receive)


@pytest.mark.asyncio
async def test_header_redaction_case_insensitive(caplog, monkeypatch):
    monkeypatch.setattr(settings, "app_debug", True)

    headers = [
        ("Authorization", "Bearer sensitive_token"),
        ("authorization", "Bearer another_sensitive"),
        ("Proxy-Authorization", "Basic secret_proxy"),
        ("Cookie", "session=abcdef"),
        ("Set-Cookie", "session=12345"),
        ("X-Api-Key", "api-key-value"),
        ("Non-Sensitive-Header", "safe_value"),
    ]

    request = create_mock_request(headers=headers)

    caplog.set_level(logging.DEBUG)
    await log_exception(request, Exception("Test Exception"))

    # Extract log message that contains the curl command
    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 1
    curl_cmd = curl_logs[0]

    # Verify sensitive headers are redacted
    assert "-H 'Authorization: [REDACTED]'" in curl_cmd
    assert "-H 'authorization: [REDACTED]'" in curl_cmd
    assert "-H 'Proxy-Authorization: [REDACTED]'" in curl_cmd
    assert "-H 'Cookie: [REDACTED]'" in curl_cmd
    assert "-H 'Set-Cookie: [REDACTED]'" in curl_cmd
    assert "-H 'X-Api-Key: [REDACTED]'" in curl_cmd

    # Verify non-sensitive is NOT redacted
    assert "-H 'Non-Sensitive-Header: safe_value'" in curl_cmd


@pytest.mark.asyncio
async def test_json_body_redaction_flat_and_nested(caplog, monkeypatch):
    monkeypatch.setattr(settings, "app_debug", True)

    payload = {
        "user": {
            "name": "john_doe",
            "password": "my_super_secret_password",
            "nested_secrets": {
                "token": "inner_token_xyz",
                "client_secret": "my_client_secret_123",
            },
        },
        "credentials": "top_level_credentials",
        "apikey": "my_apikey_abc",
        "normal_list": ["safe1", "safe2"],
        "nested_list_of_dicts": [
            {"safe_key": "safe_val"},
            {"secret": "hidden_secret_value"},
        ],
        "passphrase": "some_passphrase",
    }

    body_bytes = json.dumps(payload).encode("utf-8")
    request = create_mock_request(body_bytes=body_bytes)

    caplog.set_level(logging.DEBUG)
    await log_exception(request, Exception("Test Exception"))

    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 1
    curl_cmd = curl_logs[0]

    # Parse JSON from curl output to verify exact structure
    d_index = curl_cmd.find("-d '")
    assert d_index != -1
    json_part_str = curl_cmd[d_index + 4 : -1]
    parsed_json = json.loads(json_part_str)

    # Verify redacted fields
    assert parsed_json["user"]["name"] == "john_doe"
    assert parsed_json["user"]["password"] == "[REDACTED]"
    assert parsed_json["user"]["nested_secrets"]["token"] == "[REDACTED]"
    assert parsed_json["user"]["nested_secrets"]["client_secret"] == "[REDACTED]"
    assert parsed_json["credentials"] == "[REDACTED]"
    assert parsed_json["apikey"] == "[REDACTED]"
    assert parsed_json["normal_list"] == ["safe1", "safe2"]
    assert parsed_json["nested_list_of_dicts"][0] == {"safe_key": "safe_val"}
    assert parsed_json["nested_list_of_dicts"][1] == {"secret": "[REDACTED]"}
    assert parsed_json["passphrase"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_malformed_and_binary_body_handling(caplog, monkeypatch):
    monkeypatch.setattr(settings, "app_debug", True)
    caplog.set_level(logging.DEBUG)

    # Case 1: Malformed JSON
    malformed_request = create_mock_request(body_bytes=b"{invalid-json-structure")
    caplog.clear()
    await log_exception(malformed_request, Exception("Test Exception 1"))
    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 1
    assert "-d '[REDACTED BINARY/MALFORMED BODY]'" in curl_logs[0]

    # Case 2: Binary data that is not decodable as UTF-8
    binary_bytes = b"\x80\x81\x82\x83\x84"
    binary_request = create_mock_request(body_bytes=binary_bytes)
    caplog.clear()
    await log_exception(binary_request, Exception("Test Exception 2"))
    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 1
    assert "-d '[REDACTED BINARY/MALFORMED BODY]'" in curl_logs[0]


@pytest.mark.asyncio
async def test_logger_disabled_when_debug_false(caplog, monkeypatch):
    monkeypatch.setattr(settings, "app_debug", False)

    request = create_mock_request()
    caplog.clear()
    await log_exception(request, Exception("Test Exception"))

    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 0


@pytest.mark.asyncio
async def test_request_stream_consumed(caplog, monkeypatch):
    monkeypatch.setattr(settings, "app_debug", True)

    request = create_mock_request()
    request._stream_consumed = True

    caplog.clear()
    await log_exception(request, Exception("Test Exception"))

    curl_logs = [r.message for r in caplog.records if "Reproduce with:" in r.message]
    assert len(curl_logs) == 0
