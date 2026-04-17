import time


class BlockedByGuardrailError(Exception):
    """
    Raised by BlockConveyCallbackHandler when `blocking=True` and a pre-flight
    guardrail check returns `blocked=True`.

    Catch this in your graph node / chain step to return a fallback response
    without invoking the underlying LLM. The exception message is the
    fallback_message returned by the PRISMtrace guardrail engine.
    """


class BlockConveyCallbackHandler:
    """
    LangChain callback handler that automatically sends traces
    to PRISMtrace for every LLM call.

    With `blocking=True`, also runs a pre-flight guardrail check before the
    model starts — if a guardrail rule with action='block' matches the last
    user message, raises BlockedByGuardrailError instead of proceeding.

    Usage:
        from blockconvey.integrations.langchain import (
            BlockConveyCallbackHandler, BlockedByGuardrailError,
        )
        from langchain_anthropic import ChatAnthropic

        handler = BlockConveyCallbackHandler(
            api_key="pt_your-key",
            project_id="your-project-id",
            agent_name="MyAgent",
            blocking=True,   # enables pre-flight guardrail check
        )
        llm = ChatAnthropic(callbacks=[handler])
    """

    def __init__(
        self,
        api_key=None,
        project_id=None,
        agent_name=None,
        agent_id=None,
        blocking: bool = False,
        fallback_message: str = "I'm not able to help with that request.",
    ):
        from blockconvey.monitor import BlockConveyMonitor
        self.monitor = BlockConveyMonitor(api_key=api_key, project_id=project_id)
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.blocking = blocking
        self.fallback_message = fallback_message
        self._start_times = {}
        self._inputs = {}

    def on_llm_start(self, serialized, prompts, run_id=None, **kwargs):
        self._start_times[str(run_id)] = time.time()
        if prompts:
            self._inputs[str(run_id)] = [
                {"role": "user", "content": p} for p in prompts
            ]

    def _last_human_content(self, messages):
        """Return the .content of the last human-typed message, or empty string."""
        last = None
        if messages:
            for msg_list in messages:
                for msg in (msg_list if isinstance(msg_list, list) else [msg_list]):
                    if getattr(msg, "type", None) == "human":
                        last = msg
        if last is None:
            return ""
        content = getattr(last, "content", "")
        # LangChain content can be a list of parts for multimodal — join text parts only.
        if isinstance(content, list):
            parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
            return " ".join(parts)
        return content if isinstance(content, str) else str(content)

    def on_chat_model_start(self, serialized, messages, run_id=None, **kwargs):
        # Pre-flight guardrail check (blocking mode). Runs BEFORE any trace
        # bookkeeping so an exception short-circuits the rest of the callback.
        if self.blocking:
            human_text = self._last_human_content(messages)
            if human_text:
                result = self.monitor.check(
                    messages=[{"role": "user", "content": human_text}],
                    direction="input",
                )
                if result.get("blocked"):
                    raise BlockedByGuardrailError(
                        result.get("fallback_message") or self.fallback_message
                    )

        self._start_times[str(run_id)] = time.time()
        input_msgs = []
        if messages:
            for msg_list in messages:
                for msg in (msg_list if isinstance(msg_list, list) else [msg_list]):
                    role = "user"
                    if hasattr(msg, "type"):
                        role = "assistant" if msg.type == "ai" else msg.type
                    content = msg.content if hasattr(msg, "content") else str(msg)
                    input_msgs.append({"role": role, "content": content})
        self._inputs[str(run_id)] = input_msgs

    def on_llm_end(self, response, run_id=None, **kwargs):
        run_key = str(run_id)
        start = self._start_times.pop(run_key, time.time())
        latency_ms = int((time.time() - start) * 1000)
        inputs = self._inputs.pop(run_key, [])

        output = ""
        if response.generations:
            gen = response.generations[0][0]
            output = gen.text if hasattr(gen, "text") else str(gen)

        model = "unknown"
        if hasattr(response, "llm_output") and response.llm_output:
            model = response.llm_output.get("model_name", "unknown")

        tokens_in = 0
        tokens_out = 0
        if hasattr(response, "llm_output") and response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            tokens_in = usage.get("prompt_tokens", 0)
            tokens_out = usage.get("completion_tokens", 0)

        if isinstance(inputs, list) and inputs and isinstance(inputs[0], dict):
            input_messages = inputs
        else:
            input_messages = [{"role": "user", "content": str(inputs)}]

        self.monitor.trace(
            input_messages=input_messages,
            output_message=output,
            model=model,
            latency_ms=latency_ms,
            token_count_input=tokens_in,
            token_count_output=tokens_out,
            agent_name=self.agent_name,
            agent_id=self.agent_id,
        )

    def on_llm_error(self, error, run_id=None, **kwargs):
        self._start_times.pop(str(run_id), None)
        self._inputs.pop(str(run_id), None)

    def on_chain_start(self, *args, **kwargs): pass
    def on_chain_end(self, *args, **kwargs): pass
    def on_chain_error(self, *args, **kwargs): pass
    def on_tool_start(self, *args, **kwargs): pass
    def on_tool_end(self, *args, **kwargs): pass
    def on_tool_error(self, *args, **kwargs): pass
    def on_agent_action(self, *args, **kwargs): pass
    def on_agent_finish(self, *args, **kwargs): pass
    def on_text(self, *args, **kwargs): pass
