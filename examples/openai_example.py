"""
OpenAI and Anthropic integration examples.

pip install blockconvey-monitor[openai]
pip install blockconvey-monitor[anthropic]
"""

import os
from blockconvey import monitor

prism = monitor(
    api_key=os.getenv("BLOCKCONVEY_API_KEY"),
    project_id=os.getenv("BLOCKCONVEY_PROJECT_ID"),
)

# --- OpenAI ---
# pip install openai
# import openai
# from blockconvey.integrations.openai import wrap_openai
#
# client = wrap_openai(openai.OpenAI(), prism)
#
# Every call below is auto-traced:
# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[{"role": "user", "content": "Explain model risk management."}],
# )
# print(response.choices[0].message.content)


# --- Anthropic ---
# pip install anthropic
# import anthropic
# from blockconvey.integrations.anthropic import wrap_anthropic
#
# client = wrap_anthropic(anthropic.Anthropic(), prism)
#
# Every call below is auto-traced:
# response = client.messages.create(
#     model="claude-sonnet-4-6",
#     max_tokens=1024,
#     messages=[{"role": "user", "content": "What is SR 11-7?"}],
# )
# print(response.content[0].text)


# --- Via monitor convenience methods ---
# import openai
# client = prism.monitor_openai(openai.OpenAI())
#
# import anthropic
# client = prism.monitor_anthropic(anthropic.Anthropic())

print("Integration examples ready — uncomment to use with real API keys.")
