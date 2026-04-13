import pytest
import threading
from unittest.mock import patch, MagicMock

from blockconvey.monitor import BlockConveyMonitor, monitor
from blockconvey.trace import Trace, Message
from blockconvey.decorators import traced


# ---------------------------------------------------------------------------
# BlockConveyMonitor init
# ---------------------------------------------------------------------------

def test_init_with_explicit_args():
    m = BlockConveyMonitor(api_key="test-key", project_id="test-project")
    assert m.api_key == "test-key"
    assert m.project_id == "test-project"


def test_init_from_env(monkeypatch):
    monkeypatch.setenv("BLOCKCONVEY_API_KEY", "env-key")
    monkeypatch.setenv("BLOCKCONVEY_PROJECT_ID", "env-project")
    m = BlockConveyMonitor()
    assert m.api_key == "env-key"
    assert m.project_id == "env-project"


def test_init_fallback_prismtrace_env(monkeypatch):
    monkeypatch.setenv("PRISMTRACE_API_KEY", "pt-key")
    monkeypatch.setenv("PRISMTRACE_PROJECT_ID", "pt-project")
    m = BlockConveyMonitor()
    assert m.api_key == "pt-key"
    assert m.project_id == "pt-project"


def test_init_missing_api_key():
    with pytest.raises(ValueError, match="api_key required"):
        BlockConveyMonitor(project_id="proj")


def test_init_missing_project_id():
    with pytest.raises(ValueError, match="project_id required"):
        BlockConveyMonitor(api_key="key")


def test_convenience_monitor_function():
    m = monitor(api_key="k", project_id="p")
    assert isinstance(m, BlockConveyMonitor)


# ---------------------------------------------------------------------------
# Trace sending
# ---------------------------------------------------------------------------

def test_trace_sync_success():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=False)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"trace_id": "abc-123"}

    with patch("httpx.post", return_value=mock_response) as mock_post:
        trace_id = m.trace(
            input_messages=[{"role": "user", "content": "Hello"}],
            output_message="Hi there",
            model="gpt-4o",
            latency_ms=500,
        )

    assert trace_id == "abc-123"
    called_payload = mock_post.call_args[1]["json"]
    assert called_payload["model"] == "gpt-4o"
    assert called_payload["project_id"] == "p"


def test_trace_sync_http_error():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=False)
    mock_response = MagicMock()
    mock_response.status_code = 500

    with patch("httpx.post", return_value=mock_response):
        result = m.trace(
            input_messages=[{"role": "user", "content": "Hello"}],
            output_message="Hi",
        )

    assert result is None


def test_trace_sync_network_exception():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=False)

    with patch("httpx.post", side_effect=Exception("Connection refused")):
        result = m.trace(
            input_messages=[{"role": "user", "content": "Hello"}],
            output_message="Hi",
        )

    assert result is None


def test_trace_async_returns_none():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=True)

    with patch.object(m, "_send", return_value="trace-id") as mock_send:
        result = m.trace(
            input_messages=[{"role": "user", "content": "Hello"}],
            output_message="Hi",
        )

    assert result is None  # async mode always returns None immediately


def test_trace_metadata_merging():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=False)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"trace_id": "x"}

    with patch("httpx.post", return_value=mock_response) as mock_post:
        m.trace(
            input_messages=[{"role": "user", "content": "Hi"}],
            output_message="Hello",
            agent_name="TestAgent",
            agent_id="agent-001",
            session_id="sess-1",
            metadata={"custom_key": "custom_val"},
        )

    payload = mock_post.call_args[1]["json"]
    assert payload["metadata"]["agent_name"] == "TestAgent"
    assert payload["metadata"]["agent_id"] == "agent-001"
    assert payload["metadata"]["session_id"] == "sess-1"
    assert payload["metadata"]["custom_key"] == "custom_val"


# ---------------------------------------------------------------------------
# Trace dataclass
# ---------------------------------------------------------------------------

def test_trace_to_payload():
    t = Trace(
        input_messages=[Message("user", "What is my balance?")],
        output_message="$1,234",
        model="claude-sonnet-4-6",
        latency_ms=300,
        agent_name="BankBot",
    )
    payload = t.to_payload("proj-1", "key-1")
    assert payload["input_messages"] == [{"role": "user", "content": "What is my balance?"}]
    assert payload["metadata"]["agent_name"] == "BankBot"
    assert payload["model"] == "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# @traced decorator
# ---------------------------------------------------------------------------

def test_traced_decorator():
    m = BlockConveyMonitor(api_key="k", project_id="p", async_mode=False)
    captured = {}

    def fake_trace(**kwargs):
        captured.update(kwargs)
        return "trace-id"

    m.trace = fake_trace

    @traced(m, agent_name="Advisor", model="gpt-4o")
    def ask(user_message: str) -> str:
        return "The answer is 42"

    result = ask("What is the answer?")

    assert result == "The answer is 42"
    assert captured["agent_name"] == "Advisor"
    assert captured["model"] == "gpt-4o"
    assert captured["input_messages"] == [{"role": "user", "content": "What is the answer?"}]
    assert captured["output_message"] == "The answer is 42"
    assert captured["latency_ms"] >= 0
