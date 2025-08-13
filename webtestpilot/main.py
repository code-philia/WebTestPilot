from dotenv import load_dotenv
from baml_py import ClientRegistry

load_dotenv()

cr = ClientRegistry()
cr.set_primary("GPT4o")

# TODO: Unified way to manage clientregistry for each llm function call

# TODO: Main loop of parser + executor

# TODO: Run experiments
