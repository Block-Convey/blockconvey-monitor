from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import time


@dataclass
class Message:
    role: str
    content: str

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}


@dataclass
class Trace:
    """
    Represents a single LLM interaction to be sent to PRISMtrace.

    Usage:
        trace = Trace(
            input_messages=[Message("user", "What is my balance?")],
            output_message="Your balance is $1,234.56.",
            model="gpt-4o",
            latency_ms=850,
        )
    """
    input_messages: List[Message]
    output_message: str
    model: str = "unknown"
    latency_ms: int = 0
    token_count_input: int = 0
    token_count_output: int = 0
    agent_name: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_payload(self, project_id: str, api_key: str) -> Dict:
        return {
            "project_id": project_id,
            "api_key": api_key,
            "input_messages": [
                m.to_dict() if isinstance(m, Message) else m
                for m in self.input_messages
            ],
            "output_message": self.output_message,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "token_count_input": self.token_count_input,
            "token_count_output": self.token_count_output,
            "metadata": {
                **self.metadata,
                **({"agent_name": self.agent_name} if self.agent_name else {}),
                **({"agent_id": self.agent_id} if self.agent_id else {}),
                **({"session_id": self.session_id} if self.session_id else {}),
            },
        }
