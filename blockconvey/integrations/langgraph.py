from blockconvey.integrations.langchain import (
    BlockConveyCallbackHandler as LangChainHandler,
    BlockedByGuardrailError,
)

__all__ = ["BlockConveyCallbackHandler", "BlockedByGuardrailError"]


class BlockConveyCallbackHandler(LangChainHandler):
    """
    LangGraph callback handler. Same as LangChain handler but
    designed for graph-based agent workflows.

    Each graph node execution is traced as a separate step,
    giving full visibility into the agent's decision chain.

    With `blocking=True`, also performs a pre-flight guardrail check before
    each chat-model invocation and raises `BlockedByGuardrailError` when a
    rule with action='block' matches.

    Usage:
        from blockconvey.integrations.langgraph import (
            BlockConveyCallbackHandler, BlockedByGuardrailError,
        )
        from langgraph.graph import StateGraph

        handler = BlockConveyCallbackHandler(
            api_key="pt_your-key",
            project_id="your-project-id",
            agent_name="LoanProcessingGraph",
            blocking=True,
        )
        graph.invoke(state, config={"callbacks": [handler]})
    """
    pass  # LangGraph uses LangChain's callback interface
