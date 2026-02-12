# RQ1 Experiment

This experiment evaluates the ability of different test methods to complete normal tasks on the target web applications.

## Running the Experiment

1. Execute the `run.sh` script with the desired **METHOD** and **APPLICATION** as arguments:

    ```bash
    ./run.sh METHOD APPLICATION
    ```

2. Allowed values:

    * **METHOD**: `webtestpilot`, `pinata`, `naviqate`, `lavague`
    * **APPLICATION**: `bookstack`, `invoiceninja`, `indico`, `prestashop`

3. Output:

    Results will be saved in a directory named:

    ```
    ./results/METHOD_APPLICATION
    ```

    relative to the script location.
    For example:

    ```bash
    ./results/lavague_indico
    ```

    contains the evaluation results of the `lavague` method on the `indico` application.