# RQ3 Experiment

This experiment evaluates the robustness of WebTestPilot against different types of natural language test descriptions as input.

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