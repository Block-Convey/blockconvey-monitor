"""
LangChain / LangGraph integration example.

pip install blockconvey-monitor[langchain] langchain-anthropic
"""

# LangChain
from blockconvey.integrations.langchain import BlockConveyCallbackHandler

handler = BlockConveyCallbackHandler(
    api_key="pt_your-key",           # or set BLOCKCONVEY_API_KEY
    project_id="your-project-id",    # or set BLOCKCONVEY_PROJECT_ID
    agent_name="ComplianceAdvisor",
    agent_id="compliance-advisor-v1",
)

# Attach to any LangChain LLM
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-sonnet-4-6", callbacks=[handler])
# response = llm.invoke("Summarize BSA requirements for wire transfers")
# All calls to llm.invoke() are now automatically traced.


# LangGraph
from blockconvey.integrations.langgraph import BlockConveyCallbackHandler as GraphHandler

graph_handler = GraphHandler(
    api_key="pt_your-key",
    project_id="your-project-id",
    agent_name="LoanProcessingGraph",
)

# from langgraph.graph import StateGraph
# graph = StateGraph(...)
# graph.invoke(initial_state, config={"callbacks": [graph_handler]})
# Each node's LLM call is individually traced.

print("LangChain handler configured:", handler.agent_name)
print("LangGraph handler configured:", graph_handler.agent_name)
