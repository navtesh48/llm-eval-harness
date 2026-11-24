"""A tiny 'LLM app' used by the end-to-end tests. FAKE_MODE=bad simulates a prompt change that hurts quality."""
import os
CALLS = {'n': 0}

def answer(text: str) -> str:
    CALLS['n'] += 1
    if os.getenv('FAKE_MODE') == 'bad':
        return 'idk'
    return {'ph?': 'Chlorella prefers pH 7 to 8.', 'temp?': 'Around 28 degrees Celsius.'}.get(text, 'unknown')
