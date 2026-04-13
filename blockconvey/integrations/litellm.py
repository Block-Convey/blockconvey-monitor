"""
LiteLLM integration for blockconvey-monitor.

Usage:
    from blockconvey.integrations.litellm import instrument_litellm
    from blockconvey import monitor

    prism = monitor()
    instrument_litellm(prism)

    import litellm
    response = litellm.completion(model="gpt-4o", messages=messages)
"""
import time


def instrument_litellm(monitor_instance) -> bool:
    """
    Monkey-patch litellm.completion to auto-trace all calls.
    Returns True if litellm is installed, False if not.
    """
    try:
        import litellm

        original_completion = litellm.completion

        def traced_completion(*args, **kwargs):
            start = time.time()
            response = original_completion(*args, **kwargs)
            latency_ms = int((time.time() - start) * 1000)

            messages = kwargs.get("messages", [])
            model = kwargs.get("model", "unknown")
            output = ""
            tokens_in = 0
            tokens_out = 0

            if response.choices:
                output = response.choices[0].message.content or ""
            if response.usage:
                tokens_in = response.usage.prompt_tokens
                tokens_out = response.usage.completion_tokens

            monitor_instance.trace(
                input_messages=messages,
                output_message=output,
                model=model,
                latency_ms=latency_ms,
                token_count_input=tokens_in,
                token_count_output=tokens_out,
            )
            return response

        litellm.completion = traced_completion
        return True
    except ImportError:
        return False
