## Setup Baseline
```
cd ./$BASELINE
uv sync
```

## Run Baselines
```
source ./$BASELINE/.venv/bin/activate
python evaluate.py $BASELINE $APP --headless --test_dir ... --output_dir ...
```

$BASELINE can be one of `lavague`, `naviqate`, `pinata`, `webtestpilot`
$APP can be one of `bookstack`, `invoiceninja`, `indico`, `prestashop`