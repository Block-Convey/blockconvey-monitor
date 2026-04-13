import time


class BlockConveyCallbackHandler:
    """
    LangChain callback handler that automatically sends traces
    to PRISMtrace for every LLM call.

    Usage:
        from blockconvey.integrations.langchain import BlockConveyCallbackHandler
        from langchain_anthropic import ChatAnthropic

        handler = BlockConveyCallbackHandler(
            api_key="pt_your-key",
            project_id="your-project-id",
            agent_name="MyAgent"
        )
        llm = ChatAnthropic(callbacks=[handler])
    """

    def __init__(
        self,
        api_key=None,
        project_id=None,
        agent_name=None,
        agent_id=None,
    ):
        from blockconvey.monitor import BlockConveyMonitor
        self.monitor = BlockConveyMonitor(api_key=api_key, project_id=project_id)
        self.agent_name = agent_name
        self.agent_id = agent_id
        self._start_times = {}
        self._inputs = {}

    def on_llm_start(self, serialized, prompts, run_id=None, **kwargs):
        self._start_times[str(run_id)] = time.time()
        self._inputs[str(run_id)] = prompts

    def on_chat_model_start(self, serialized, messages, run_id=None, **kwargs):
        self._start_times[str(run_id)] = time.time()
        input_msgs = []
        for msg_list in messages:
            for msg in msg_list:
                role = "user"
                if hasattr(msg, "type"):
                    role = "assistant" if msg.type == "ai" else msg.type
                input_msgs.append({
                    "role": role,
                    "content": msg.content if hasattr(msg, "content") else str(msg),
                })
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
