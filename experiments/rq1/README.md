# RQ1 Experiment

This experiment evaluates the ability of different test methods to complete normal tasks on the target web applications.

## Running the Experiment

1. Run the `rq1` recipe with the desired **METHOD** and **APPLICATION**:

    ```bash
    just run rq1 METHOD APPLICATION
    ```

    Or run every method on every application in sequence (failed combinations are listed at the end):

    ```bash
    just run rq1-all
    ```

2. Allowed values:

    * **METHOD**: `webtestpilot`, `pinata`, `naviqate`, `lavague`
    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`

3. Output:

    Results will be saved in a directory named:

    ```
    ./results/METHOD_APPLICATION
    ```

    relative to `experiments/rq1`. A log of the run is saved alongside the results.
    For example:

    ```bash
    ./results/lavague_indico
    ```

    contains the evaluation results of the `lavague` method on the `indico` application.