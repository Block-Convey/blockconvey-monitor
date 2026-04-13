import time
import functools


def wrap_openai(client, monitor_instance):
    """
    Wrap an OpenAI client to automatically trace all completions.

    Usage:
        import openai
        from blockconvey import monitor
        from blockconvey.integrations.openai import wrap_openai

        prism = monitor()
        client = wrap_openai(openai.OpenAI(), prism)

        # Now all client.chat.completions.create() calls are auto-traced
    """
    original_create = client.chat.completions.create

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

    client.chat.completions.create = traced_create
    return client
