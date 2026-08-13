import re

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from clinical_mdr_api.main import app as main_app
from consumer_api.consumer_api import app as consumer_app
from extensions.extensions_api import app as extensions_app


def set_app_origins(app: FastAPI, origins: list[str]):
    """Helper function to dynamically change CORS origins for an app in tests"""
    for middleware in app.user_middleware:
        if middleware.cls is CORSMiddleware:
            middleware.kwargs["allow_origins"] = origins
            # Remove allow_origin_regex if present to ensure strict explicit whitelisting
            if "allow_origin_regex" in middleware.kwargs:
                middleware.kwargs["allow_origin_regex"] = None
    # Reset middleware stack to force rebuild with new configuration on next request
    app.middleware_stack = None


def get_test_paths(app: FastAPI) -> list[tuple[str, str]]:
    """Dynamically query the active routing table of the FastAPI application"""
    paths = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            for method in route.methods:
                if method.upper() == "OPTIONS":
                    continue
                # Format path to replace path parameters (e.g. {sn} with '1')
                formatted_path = re.sub(r"\{[a-zA-Z_0-9:]+\}", "1", route.path)
                paths.append((formatted_path, method.upper()))
    return paths


def test_main_app_cors_all_routes():
    """Verify CORS headers across all routes dynamically queried from main_app routing table"""
    trusted_origins = [
        "https://trusted-portal.clinical.example.com",
        "http://localhost:5005",
    ]
    set_app_origins(main_app, trusted_origins)

    client = TestClient(main_app)
    paths = get_test_paths(main_app)

    assert len(paths) > 0, "No routes found in main_app"

    for path, method in paths:
        # 1. Authorized Origin Preflight
        for trusted_origin in trusted_origins:
            headers = {
                "Origin": trusted_origin,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            }
            response = client.options(path, headers=headers)
            assert response.status_code in (
                200,
                204,
            ), f"Preflight failed for path {path} with status {response.status_code}"
            assert (
                response.headers.get("access-control-allow-origin") == trusted_origin
            ), f"CORS origin not allowed for {path}"
            assert (
                response.headers.get("access-control-allow-credentials") == "true"
            ), f"CORS credentials not allowed for {path}"

        # 2. Unauthorized Origin Preflight
        untrusted_headers = {
            "Origin": "https://untrusted-attacker.com",
            "Access-Control-Request-Method": method,
        }
        response = client.options(path, headers=untrusted_headers)
        assert (
            "access-control-allow-origin" not in response.headers
        ), f"Untrusted origin allowed for path {path}"


def test_consumer_app_cors_all_routes():
    """Verify CORS headers across all routes dynamically queried from consumer_app routing table"""
    trusted_origins = ["https://trusted-portal.clinical.example.com"]
    set_app_origins(consumer_app, trusted_origins)

    client = TestClient(consumer_app)
    paths = get_test_paths(consumer_app)

    assert len(paths) > 0, "No routes found in consumer_app"

    for path, method in paths:
        # 1. Authorized Origin Preflight
        for trusted_origin in trusted_origins:
            headers = {
                "Origin": trusted_origin,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            }
            response = client.options(path, headers=headers)
            assert response.status_code in (200, 204)
            assert response.headers.get("access-control-allow-origin") == trusted_origin
            assert response.headers.get("access-control-allow-credentials") == "true"

        # 2. Unauthorized Origin Preflight
        untrusted_headers = {
            "Origin": "https://untrusted-attacker.com",
            "Access-Control-Request-Method": method,
        }
        response = client.options(path, headers=untrusted_headers)
        assert "access-control-allow-origin" not in response.headers


def test_extensions_app_cors_all_routes():
    """Verify CORS headers across all routes dynamically queried from extensions_app routing table"""
    trusted_origins = ["https://trusted-portal.clinical.example.com"]
    set_app_origins(extensions_app, trusted_origins)

    client = TestClient(extensions_app)
    paths = get_test_paths(extensions_app)

    assert len(paths) > 0, "No routes found in extensions_app"

    for path, method in paths:
        # 1. Authorized Origin Preflight
        for trusted_origin in trusted_origins:
            headers = {
                "Origin": trusted_origin,
                "Access-Control-Request-Method": method,
                "Access-Control-Request-Headers": "content-type",
            }
            response = client.options(path, headers=headers)
            assert response.status_code in (200, 204)
            assert response.headers.get("access-control-allow-origin") == trusted_origin
            assert response.headers.get("access-control-allow-credentials") == "true"

        # 2. Unauthorized Origin Preflight
        untrusted_headers = {
            "Origin": "https://untrusted-attacker.com",
            "Access-Control-Request-Method": method,
        }
        response = client.options(path, headers=untrusted_headers)
        assert "access-control-allow-origin" not in response.headers


def test_cors_simple_request_main_app():
    """Verify that simple requests also return correct CORS headers when authorized"""
    trusted_origins = ["https://trusted-portal.clinical.example.com"]
    set_app_origins(main_app, trusted_origins)

    client = TestClient(main_app)
    path = "/feature-flags"

    # Authorized Simple Request
    response = client.get(
        path, headers={"Origin": "https://trusted-portal.clinical.example.com"}
    )
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://trusted-portal.clinical.example.com"
    )
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert (
        "traceresponse"
        in response.headers.get("access-control-expose-headers", "").lower()
    )

    # Unauthorized Simple Request
    response = client.get(path, headers={"Origin": "https://untrusted-attacker.com"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_simple_request_consumer_app():
    """Verify that simple requests to consumer_app return correct CORS headers when authorized"""
    trusted_origins = ["https://trusted-portal.clinical.example.com"]
    set_app_origins(consumer_app, trusted_origins)

    client = TestClient(consumer_app)
    path = "/system/information"

    # Authorized Simple Request
    response = client.get(
        path, headers={"Origin": "https://trusted-portal.clinical.example.com"}
    )
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://trusted-portal.clinical.example.com"
    )
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert (
        "traceresponse"
        in response.headers.get("access-control-expose-headers", "").lower()
    )

    # Unauthorized Simple Request
    response = client.get(path, headers={"Origin": "https://untrusted-attacker.com"})
    assert "access-control-allow-origin" not in response.headers


def test_cors_simple_request_extensions_app():
    """Verify that simple requests to extensions_app return correct CORS headers when authorized"""
    trusted_origins = ["https://trusted-portal.clinical.example.com"]
    set_app_origins(extensions_app, trusted_origins)

    client = TestClient(extensions_app)
    path = "/system/healthcheck"

    # Authorized Simple Request
    response = client.get(
        path, headers={"Origin": "https://trusted-portal.clinical.example.com"}
    )
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://trusted-portal.clinical.example.com"
    )
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert (
        "traceresponse"
        in response.headers.get("access-control-expose-headers", "").lower()
    )

    # Unauthorized Simple Request
    response = client.get(path, headers={"Origin": "https://untrusted-attacker.com"})
    assert "access-control-allow-origin" not in response.headers
