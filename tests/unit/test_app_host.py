import pytest

# The demo app needs the web extra
pytest.importorskip("flask")

from pymaskinporten import app as app_module


@pytest.fixture
def run_kwargs(monkeypatch):
    """Capture the arguments main() passes to app.run instead of starting a server."""
    captured = {}
    monkeypatch.setattr(app_module.app, "run", lambda **kwargs: captured.update(kwargs))
    return captured


@pytest.mark.unit
def test_main_binds_localhost_by_default(monkeypatch, run_kwargs):
    monkeypatch.delenv("FLASK_RUN_HOST", raising=False)

    app_module.main()

    assert run_kwargs["host"] == "127.0.0.1"


@pytest.mark.unit
def test_main_host_can_be_overridden(monkeypatch, run_kwargs):
    monkeypatch.setenv("FLASK_RUN_HOST", "0.0.0.0")

    app_module.main()

    assert run_kwargs["host"] == "0.0.0.0"
