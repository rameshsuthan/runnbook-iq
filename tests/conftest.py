import socket
import pytest


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Ordinary tests must not access the network")
    monkeypatch.setattr(socket.socket, "connect", denied)
    for key in ("PINECONE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(key, raising=False)
