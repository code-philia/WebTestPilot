### Start the (local) remote browser
Might have to check and install Google Chrome at local before.

```bash
source browser.sh
```


### Setup WebTestPilot runtime
Setup .env variables (if using OpenAI)
```bash
cp .env.example .env
# Add in you OPEN_API_KEY
```

Setup python env
```bash
cd webtestpilot
uv sync
source ./.venv/bin/activate
python3 -V
uv run baml-cli generate
```

### Setup extension
Update latest build
```
yarn install:all
yarn package
```

Start the dev server
1. In the new window: Open file extensions.ts -> Ctrl/Command + Shift + P -> Type "Start Debugging" -> Choose
2. (Temp workaround) In the debug window, Setup the webtestpilot path at run time: Ctrl/Command + Shift + P -> Type "Enter webtestpilot workspace" -> input ....WebTestPilot/webtestpilot (fill in the whole path to folder).
3. Click the extension icon and start using.
