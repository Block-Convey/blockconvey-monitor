from typing import Optional, List, Dict, Any
import httpx
import os
import time
import threading

PRISMTRACE_URL = "https://prismtrace.blockconvey.com"


class BlockConveyMonitor:
    def __init__(
        self,
        api_key: str = None,
        project_id: str = None,
        base_url: str = None,
        async_mode: bool = True,
        timeout: int = 10,
    ):
        self.api_key = api_key or os.getenv("BLOCKCONVEY_API_KEY") or os.getenv("PRISMTRACE_API_KEY")
        self.project_id = project_id or os.getenv("BLOCKCONVEY_PROJECT_ID") or os.getenv("PRISMTRACE_PROJECT_ID")
        self.base_url = (base_url or os.getenv("PRISMTRACE_URL") or PRISMTRACE_URL).rstrip("/")
        self.async_mode = async_mode
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("api_key required. Set BLOCKCONVEY_API_KEY env var or pass api_key=")
        if not self.project_id:
            raise ValueError("project_id required. Set BLOCKCONVEY_PROJECT_ID env var or pass project_id=")

    def trace(
        self,
        input_messages: List[Dict],
        output_message: str,
        model: str = "unknown",
        latency_ms: int = 0,
        token_count_input: int = 0,
        token_count_output: int = 0,
        agent_name: str = None,
        agent_id: str = None,
        session_id: str = None,
        metadata: Dict = None,
    ) -> Optional[str]:
        """
        Send a trace to PRISMtrace.
        Returns trace_id if successful, None if failed.
        In async_mode (default), sends in background thread.
        """
        payload = {
            "project_id": self.project_id,
            "api_key": self.api_key,
            "input_messages": input_messages,
            "output_message": output_message,
            "model": model,
            "latency_ms": latency_ms,
            "token_count_input": token_count_input,
            "token_count_output": token_count_output,
            "metadata": {
                **(metadata or {}),
                **({"agent_name": agent_name} if agent_name else {}),
                **({"agent_id": agent_id} if agent_id else {}),
                **({"session_id": session_id} if session_id else {}),
            },
        }

        if self.async_mode:
            t = threading.Thread(target=self._send, args=(payload,), daemon=True)
            t.start()
            return None
        else:
            return self._send(payload)

    def _send(self, payload: dict) -> Optional[str]:
        try:
            r = httpx.post(
                f"{self.base_url}/api/traces",
                json=payload,
                timeout=self.timeout,
            )
            if r.status_code == 200:
                return r.json().get("trace_id")
        except Exception:
            pass
        return None

    def monitor_openai(self, client):
        """Wrap an OpenAI client to auto-trace all completions."""
        from blockconvey.integrations.openai import wrap_openai
        return wrap_openai(client, self)

    def monitor_anthropic(self, client):
        """Wrap an Anthropic client to auto-trace all completions."""
        from blockconvey.integrations.anthropic import wrap_anthropic
        return wrap_anthropic(client, self)


def monitor(
    api_key: str = None,
    project_id: str = None,
    **kwargs,
) -> BlockConveyMonitor:
    """Convenience constructor for BlockConveyMonitor."""
    return BlockConveyMonitor(api_key=api_key, project_id=project_id, **kwargs)
