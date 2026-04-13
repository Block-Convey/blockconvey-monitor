from typing import Optional, List, Dict
import httpx
import os

from blockconvey.monitor import BlockConveyMonitor, PRISMTRACE_URL


class AsyncBlockConveyMonitor(BlockConveyMonitor):
    """
    Async version of BlockConveyMonitor using httpx.AsyncClient.

    Usage:
        prism = AsyncBlockConveyMonitor(api_key="...", project_id="...")

        await prism.trace(
            input_messages=[{"role": "user", "content": "Hello"}],
            output_message="Hi there!",
            model="gpt-4o",
        )
    """

    async def trace(
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
        """Async trace send. Always awaited — no background thread."""
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
        return await self._async_send(payload)

    async def _async_send(self, payload: dict) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.post(
                    f"{self.base_url}/api/traces",
                    json=payload,
                )
                if r.status_code == 200:
                    return r.json().get("trace_id")
        except Exception:
            pass
        return None


def async_monitor(
    api_key: str = None,
    project_id: str = None,
    **kwargs,
) -> AsyncBlockConveyMonitor:
    """Convenience constructor for AsyncBlockConveyMonitor."""
    return AsyncBlockConveyMonitor(api_key=api_key, project_id=project_id, **kwargs)
