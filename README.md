# blockconvey-monitor

Production AI agent observability for regulated industries.

## Install

```bash
pip install blockconvey-monitor
```

## Quick start

```python
from blockconvey import monitor

prism = monitor(
    api_key="pt_your-key",
    project_id="your-project-id"
)

# Send a trace
prism.trace(
    input_messages=[{"role": "user", "content": user_input}],
    output_message=agent_response,
    model="gpt-4o",
    latency_ms=1200,
    agent_name="Customer Service Agent"
)
```

## With decorator

```python
from blockconvey import monitor, traced

prism = monitor()

@traced(prism, agent_name="LoanAdvisor", model="claude-sonnet-4-6")
def ask_agent(user_message: str) -> str:
    return your_llm_call(user_message)
```

## Async

```python
from blockconvey import async_monitor

prism = async_monitor()

await prism.trace(
    input_messages=[{"role": "user", "content": user_input}],
    output_message=agent_response,
    model="gpt-4o",
)
```

## Environment variables

```bash
BLOCKCONVEY_API_KEY=pt_your-key
BLOCKCONVEY_PROJECT_ID=your-project-id
```

## Integrations

### LangChain / LangGraph

```bash
pip install blockconvey-monitor[langchain]
```

```python
from blockconvey.integrations.langchain import BlockConveyCallbackHandler
from langchain_anthropic import ChatAnthropic

handler = BlockConveyCallbackHandler(
    api_key="pt_your-key",
    project_id="your-project-id",
    agent_name="MyAgent"
)
llm = ChatAnthropic(model="claude-sonnet-4-6", callbacks=[handler])
# All llm.invoke() calls are now automatically traced
```

```python
# LangGraph
from blockconvey.integrations.langgraph import BlockConveyCallbackHandler

handler = BlockConveyCallbackHandler(agent_name="LoanProcessingGraph")
graph.invoke(state, config={"callbacks": [handler]})
```

### OpenAI

```bash
pip install blockconvey-monitor[openai]
```

```python
import openai
from blockconvey import monitor
from blockconvey.integrations.openai import wrap_openai

prism = monitor()
client = wrap_openai(openai.OpenAI(), prism)

# All client.chat.completions.create() calls are now auto-traced
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain model risk management."}],
)
```

### Anthropic

```bash
pip install blockconvey-monitor[anthropic]
```

```python
import anthropic
from blockconvey import monitor
from blockconvey.integrations.anthropic import wrap_anthropic

prism = monitor()
client = wrap_anthropic(anthropic.Anthropic(), prism)

# All client.messages.create() calls are now auto-traced
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is SR 11-7?"}],
)
```

### Install all integrations

```bash
pip install blockconvey-monitor[all]
```

## Docs

https://docs.blockconvey.com
