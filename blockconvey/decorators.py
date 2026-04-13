import time
import functools
from typing import Callable


def traced(
    monitor_instance,
    agent_name: str = None,
    agent_id: str = None,
    model: str = "unknown",
):
    """
    Decorator to automatically trace an LLM call function.

    Usage:
        @traced(prism, agent_name="CustomerService", model="gpt-4o")
        def ask_agent(user_message: str) -> str:
            return openai_client.chat(...)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            latency_ms = int((time.time() - start) * 1000)

            # Extract user message from first arg or kwargs
            user_msg = ""
            if args:
                user_msg = str(args[0])
            elif "message" in kwargs:
                user_msg = str(kwargs["message"])
            elif "user_input" in kwargs:
                user_msg = str(kwargs["user_input"])

            monitor_instance.trace(
                input_messages=[{"role": "user", "content": user_msg}],
                output_message=str(result),
                model=model,
                latency_ms=latency_ms,
                agent_name=agent_name,
                agent_id=agent_id,
            )
            return result
        return wrapper
    return decorator
