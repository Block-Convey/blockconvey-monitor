import time
import functools


def wrap_anthropic(client, monitor_instance):
    """
    Wrap an Anthropic client to automatically trace all messages.

    Usage:
        import anthropic
        from blockconvey import monitor
        from blockconvey.integrations.anthropic import wrap_anthropic

        prism = monitor()
        client = wrap_anthropic(anthropic.Anthropic(), prism)

        # Now all client.messages.create() calls are auto-traced
    """
    original_create = client.messages.create

    @functools.wraps(original_create)
    def traced_create(*args, **kwargs):
        start = time.time()
        response = original_create(*args, **kwargs)
        latency_ms = int((time.time() - start) * 1000)

        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "unknown")

        output = ""
        tokens_in = 0
        tokens_out = 0

        if response.content:
            output = (
                response.content[0].text
                if hasattr(response.content[0], "text")
                else str(response.content[0])
            )
        if response.usage:
            tokens_in = response.usage.input_tokens
            tokens_out = response.usage.output_tokens

        monitor_instance.trace(
            input_messages=messages,
            output_message=output,
            model=model,
            latency_ms=latency_ms,
            token_count_input=tokens_in,
            token_count_output=tokens_out,
        )
        return response

    client.messages.create = traced_create
    return client
