import time
import functools


def wrap_bedrock(client, monitor_instance, model_id="anthropic.claude-3-haiku-20240307-v1:0"):
    """
    Wrap an AWS Bedrock boto3 client to auto-trace all invoke_model calls.

    Usage:
        import boto3
        from blockconvey import monitor
        from blockconvey.integrations.bedrock import wrap_bedrock

        prism = monitor()
        bedrock = wrap_bedrock(
            boto3.client("bedrock-runtime", region_name="us-east-1"),
            prism
        )
        response = bedrock.invoke_model(modelId=model_id, body=json.dumps(payload))
    """
    import json
    import io

    original_invoke = client.invoke_model

    @functools.wraps(original_invoke)
    def traced_invoke(**kwargs):
        start = time.time()
        response = original_invoke(**kwargs)
        latency_ms = int((time.time() - start) * 1000)

        try:
            body = json.loads(kwargs.get("body", "{}"))
            model = kwargs.get("modelId", model_id)

            messages = body.get("messages", [])
            if not messages and "prompt" in body:
                messages = [{"role": "user", "content": body["prompt"]}]

            response_body = json.loads(response["body"].read())

            output = ""
            if "content" in response_body:
                output = response_body["content"][0].get("text", "")
            elif "completion" in response_body:
                output = response_body["completion"]

            tokens_in = response_body.get("usage", {}).get("input_tokens", 0)
            tokens_out = response_body.get("usage", {}).get("output_tokens", 0)

            monitor_instance.trace(
                input_messages=messages,
                output_message=output,
                model=model,
                latency_ms=latency_ms,
                token_count_input=tokens_in,
                token_count_output=tokens_out,
            )

            # Re-wrap response body since it's been read
            response["body"] = io.BytesIO(json.dumps(response_body).encode())
        except Exception:
            pass

        return response

    client.invoke_model = traced_invoke
    return client
