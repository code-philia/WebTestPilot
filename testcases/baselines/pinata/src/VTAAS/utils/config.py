from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent


def load_config():
    """Load environment variables from .env file."""
    # Find the root directory (where .env is located)
    root_dir = Path(__file__).resolve().parent.parent.parent.parent
    env_path = root_dir / ".env"

    # Load environment variables from .env file
    load_dotenv(dotenv_path=env_path)
