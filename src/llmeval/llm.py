import os
from anthropic import Anthropic

MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-5-5')
_client = None

def structured(schema, system: str, user: str, max_tokens: int = 1000):
    """Force the model to return an instance of the pydantic model `schema` via a tool call."""
    global _client
    if _client is None:
        _client = Anthropic()
    tool = {'name': 'emit', 'description': 'Return the verdict.', 'input_schema': schema.model_json_schema()}
    r = _client.messages.create(model=MODEL, max_tokens=max_tokens, system=system, tools=[tool],
                                tool_choice={'type': 'tool', 'name': 'emit'},
                                messages=[{'role': 'user', 'content': user}])
    return schema.model_validate(next(b for b in r.content if b.type == 'tool_use').input)
