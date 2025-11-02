# Update code
git pull

# Setup WebTestPilot + BAML
cd webtestpilot
uv sync
source ./.venv/bin/activate
python3 -V
uv run baml-cli generate

# Setup webview + extension
cd ..
yarn install:all
yarn package