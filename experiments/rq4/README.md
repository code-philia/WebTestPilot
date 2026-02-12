# RQ4 Experiment

This experiment evaluates the effectiveness of local models of different model parameter sizes on the same task

## Running the Experiment

1. Modify `method_config.yaml` so that `config_path` points to the `config.yaml` in this directory

    > **NOTE:** For local models, remember to modify .env

    ```yaml
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/local_config.yaml # For evaluating local models (Qwen2.5VL-7b to -72b)
    ```

2. Execute the `run.sh` script with the desired **APPLICATION** as arguments:

    ```bash
    ./run.sh APPLICATION
    ```

3. Allowed values:

    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`

4. Output:

    Results will be saved in a directory named:

    ```
    ./results/APPLICATION
    ```

    relative to the script location.
    For example:

    ```bash
    ./results/bookstack
    ```

    contains the evaluation results of the `bookstack` application.