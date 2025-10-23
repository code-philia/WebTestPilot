Start the (local) remote browser

Might have to check and install Google Chrome at local before.

```bash
source browser.sh
```

Setup .env variables (if using OpenAI)
```bash
cp .env.example .env
# Add in you OPEN_API_KEY
```


### Extension

Start extension dev server
```bash
cd extension
code .
```
In the new window, Ctrl/Command + Shift + P -> Type "Start Debugging" -> Choose
