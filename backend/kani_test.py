from kani import Kani, chat_in_terminal
from kani.engines.openai import OpenAIEngine

api_key = "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"
engine = OpenAIEngine(api_key, model="gpt-4o-mini")
ai = Kani(engine)
chat_in_terminal(ai)
