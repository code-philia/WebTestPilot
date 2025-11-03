# Update code
echo "Updating code repositories..."
git branch --set-upstream-to=origin/extension
git pull

# Setup WebTestPilot + BAML
echo "Setting up WebTestPilot..."
cd webtestpilot
uv sync
source ./.venv/bin/activate
python3 -V
uv run baml-cli generate

# Setup webview + extension
echo "Setting up VS Code extension..."
cd ..
yarn install:all
yarn package