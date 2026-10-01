# RQ3 Experiment

This experiment evaluates the robustness of WebTestPilot against different types of natural language test descriptions as input.

## Generating Transformed Test Cases

Transformed test cases are not checked in; generate them from the benchmark before running the experiment.

1. Set the LLM used for the `summarize` and `restyle` transformations (OpenAI-compatible endpoint) in `transform/.env` or your shell:

    ```bash
    TRANSFORM_MODEL_BASE_URL=...
    TRANSFORM_MODEL_NAME=...
    ```

2. Generate the BAML client and run the transformation for each application:

    ```bash
    cd transform
    uv run baml-cli generate
    uv run transform.py APPLICATION
    ```

    Outputs are written to `transform/APPLICATION/TRANSFORMATION/`.

## Running the Experiment

1. Modify `method_config.yaml` so that `config_path` points to the `config.yaml` in this directory

    > **NOTE:** For local models, remember to modify .env

    ```yaml
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/gpt_config.yaml   # For evaluating GPT
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/local_config.yaml # For evaluating local models (Qwen2.5VL-7b to -72b)
    ```

2. Execute the `run.sh` script with the desired **APPLICATION** and **TRANSFORMATION** as arguments:

    ```bash
    ./run.sh APPLICATION TRANSFORMATION
    ```

3. Allowed values:

    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`
    * **TRANSFORMATION**: `dropout`, `summarize`, `restyle`, `add_noise`

4. Output:

    Results will be saved in a directory named:

    ```
    ./results/APPLICATION_TRANSFORMATION
    ```

    relative to the script location.
    For example:

    ```bash
    ./results/bookstack_summarize
    ```

    contains the evaluation results of the `bookstack` application with `summarize` transformation applied.