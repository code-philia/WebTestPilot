from dotenv import load_dotenv
from baml_py import ClientRegistry

load_dotenv()

cr = ClientRegistry()
cr.set_primary("GPT4o")
