from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.routers import auth as auth_router


class DummyGoogleOAuth:
    def __init__(self):
        self.redirect_uris = []

    async def authorize_redirect(self, request, redirect_uri):
        self.redirect_uris.append(redirect_uri)
        return JSONResponse({"redirect_uri": redirect_uri})


def build_client(monkeypatch):
    app = FastAPI()
    app.include_router(auth_router.router, prefix="/admin/auth")

    dummy_google = DummyGoogleOAuth()
    monkeypatch.setattr(auth_router, "is_auth_configured", lambda: True)
    monkeypatch.setattr(auth_router, "oauth", SimpleNamespace(google=dummy_google))

    return TestClient(app), dummy_google


def test_login_uses_google_redirect_uri_override(monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_REDIRECT_URI",
        "https://sandbox-tr.ayra.network/admin/auth/callback",
    )
    monkeypatch.setattr(
        auth_router,
        "get_google_redirect_uri",
        lambda: "https://sandbox-tr.ayra.network/admin/auth/callback",
    )

    client, dummy_google = build_client(monkeypatch)
    response = client.get("/admin/auth/login")

    assert response.status_code == 200
    assert response.json()["redirect_uri"] == "https://sandbox-tr.ayra.network/admin/auth/callback"
    assert dummy_google.redirect_uris == ["https://sandbox-tr.ayra.network/admin/auth/callback"]


def test_login_falls_back_to_request_url(monkeypatch):
    monkeypatch.delenv("GOOGLE_REDIRECT_URI", raising=False)
    monkeypatch.setattr(auth_router, "get_google_redirect_uri", lambda: None)

    client, dummy_google = build_client(monkeypatch)
    response = client.get("/admin/auth/login")

    assert response.status_code == 200
    assert response.json()["redirect_uri"] == "http://testserver/admin/auth/callback"
    assert dummy_google.redirect_uris == ["http://testserver/admin/auth/callback"]
