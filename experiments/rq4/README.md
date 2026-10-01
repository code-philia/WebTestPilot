# RQ4 Experiment

This experiment evaluates the effectiveness of local models of different model parameter sizes on the same task

## Running the Experiment

1. Modify `method_config.yaml` so that `config_path` points to the `config.yaml` in this directory

    > **NOTE:** For local models, remember to modify .env

    ```yaml
    config_path: {YOUR_PATH}/webtestpilot/experiments/rq3/local_config.yaml # For evaluating local models (Qwen2.5VL-7b to -72b)
    ```

2. Run the `rq4` recipe (or `rq4-bug` to inject bugs, using `method_config.bug.yaml`) with the desired **MODEL** and **APPLICATION**:

    ```bash
    just run rq4 MODEL APPLICATION
    just run rq4-bug MODEL APPLICATION
    ```

    **MODEL** only labels the results directory; the model itself is chosen by `config_path` in step 1.

3. Allowed values:

    * **MODEL**: `qwen-3b`, `qwen-7b`, `qwen-32b`, `qwen-72b`
    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`

4. Output:

    Results will be saved in a directory named:

    ```
    ./results/MODEL_APPLICATION   # bug_MODEL_APPLICATION for rq4-bug
    ```

    relative to `experiments/rq4`. A log of the run is saved alongside the results.
    For example:

    ```bash
    ./results/qwen-7b_bookstack
    ```

    contains the evaluation results of Qwen2.5-VL-7B on the `bookstack` application.