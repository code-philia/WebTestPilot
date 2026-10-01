# RQ2 Experiment

This experiment evaluates the ability of different test methods with assertion capabilities to detect injected bugs during task execution on the target web applications.

## Running the Experiment

1. Run the `rq2` recipe with the desired **METHOD** and **APPLICATION**:

    ```bash
    just run rq2 METHOD APPLICATION
    ```

    Or run every method on every application in sequence (failed combinations are listed at the end):

    ```bash
    just run rq2-all
    ```

2. Allowed values:

    * **METHOD**: `webtestpilot`, `pinata`
    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`

3. Output:

    Results will be saved in a directory named:

    ```
    ./results/METHOD_APPLICATION
    ```

    relative to `experiments/rq2`. A log of the run is saved alongside the results.
    For example:

    ```bash
    ./results/webtestpilot_bookstack
    ```

    contains the evaluation results of the `webtestpilot` method on the `bookstack` application.