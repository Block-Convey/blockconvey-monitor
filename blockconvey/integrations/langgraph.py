from blockconvey.integrations.langchain import BlockConveyCallbackHandler as LangChainHandler


class BlockConveyCallbackHandler(LangChainHandler):
    """
    LangGraph callback handler. Same as LangChain handler but
    designed for graph-based agent workflows.

    Each graph node execution is traced as a separate step,
    giving full visibility into the agent's decision chain.

    Usage:
        from blockconvey.integrations.langgraph import BlockConveyCallbackHandler
        from langgraph.graph import StateGraph

        handler = BlockConveyCallbackHandler(
            api_key="pt_your-key",
            project_id="your-project-id",
            agent_name="LoanProcessingGraph"
        )
        graph.invoke(state, config={"callbacks": [handler]})
    """
    pass  # LangGraph uses LangChain's callback interface
