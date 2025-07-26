from openai import OpenAI
import os
import openai

print(openai.__file__)
print(openai.__version__)


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
response = client.chat.completions.create(
    model="qwen/qwen3-235b-a22b:free",
    messages=[{"role": "user", "content": "hello, world!"}],
)
print(response.choices[0].message.content)
