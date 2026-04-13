"""
Basic blockconvey-monitor usage.

Set env vars before running:
  export BLOCKCONVEY_API_KEY=pt_your-key
  export BLOCKCONVEY_PROJECT_ID=your-project-id
"""

import time
from blockconvey import monitor, traced

# Initialize
prism = monitor()  # reads from env vars

# --- Manual trace ---
start = time.time()
user_input = "What is the status of my loan application?"
agent_response = "Your application is under review. Expected decision: 3 business days."
latency = int((time.time() - start) * 1000)

prism.trace(
    input_messages=[{"role": "user", "content": user_input}],
    output_message=agent_response,
    model="claude-sonnet-4-6",
    latency_ms=latency,
    token_count_input=22,
    token_count_output=18,
    agent_name="LoanAdvisor",
    agent_id="loan-advisor-v2",
    session_id="sess-abc123",
    metadata={"department": "retail_lending", "channel": "web"},
)
print("Trace sent (async background thread)")

# --- Decorator usage ---
@traced(prism, agent_name="CustomerService", model="gpt-4o")
def ask_agent(user_message: str) -> str:
    # Simulated LLM call
    time.sleep(0.1)
    return "Thank you for contacting us. How can I help?"

response = ask_agent("I need help with my account.")
print(f"Agent response: {response}")

# --- Sync mode (blocks until trace sent) ---
prism_sync = monitor(async_mode=False)
trace_id = prism_sync.trace(
    input_messages=[{"role": "user", "content": "Check balance"}],
    output_message="Your balance is $5,200.",
    model="gpt-4o-mini",
    latency_ms=320,
)
print(f"Sync trace_id: {trace_id}")
