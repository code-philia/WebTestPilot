# RQ3 Experiment

This experiment evaluates the robustness of WebTestPilot against different types of natural language test descriptions as input.

## Generating Transformed Test Cases

Transformed test cases are not checked in; generate them from the benchmark before running the experiment.

1. Set the LLM used for the `summarize` and `restyle` transformations (OpenAI-compatible endpoint) in `transform/.env` or your shell:

    ```bash
    TRANSFORM_MODEL_BASE_URL=...
    TRANSFORM_MODEL_NAME=...
    ```

2. Generate the transformed test cases for each application:

    ```bash
    just run rq3-transform APPLICATION
    ```

    Outputs are written to `transform/APPLICATION/TRANSFORMATION/`.

## Running the Experiment

1. Modify `method_config.yaml` so that `config_path` points to the `config.yaml` in this directory

    > **NOTE:** For local models, remember to modify .env

    ```yaml
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/gpt_config.yaml   # For evaluating GPT
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/local_config.yaml # For evaluating local models (Qwen2.5VL-7b to -72b)
    ```

2. Run the `rq3` recipe (or `rq3-bug` to inject bugs, using `method_config.bug.yaml`) with the desired **MODEL**, **APPLICATION**, and **TRANSFORMATION**:

    ```bash
    just run rq3 MODEL APPLICATION TRANSFORMATION
    just run rq3-bug MODEL APPLICATION TRANSFORMATION
    ```

    **MODEL** only labels the results directory; the model itself is chosen by `config_path` in step 1.

3. Allowed values:

    * **MODEL**: `gpt`, `qwen-3b`, `qwen-7b`, `qwen-32b`, `qwen-72b`
    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`
    * **TRANSFORMATION**: `dropout`, `summarize`, `restyle`, `add_noise`

4. Output:

    Results will be saved in a directory named:

    ```
    ./results/MODEL_APPLICATION_TRANSFORMATION   # bug_MODEL_APPLICATION_TRANSFORMATION for rq3-bug
    ```

    relative to `experiments/rq3`. A log of the run is saved alongside the results.
    For example:

    ```bash
    ./results/gpt_bookstack_summarize
    ```

    contains the evaluation results of GPT on the `bookstack` application with the `summarize` transformation applied.