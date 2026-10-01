# Experiment recipes, run from the repository root as `just run <recipe> ...`.
# Recipes in this module run with `experiments/` as their working directory.

set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

root := justfile_directory()
benchmark := root / "benchmark"
experiments := source_directory()
webtestpilot_venv := root / "webtestpilot" / ".venv"

methods := "webtestpilot pinata lavague naviqate"
assertion_methods := "webtestpilot pinata"
applications := "bookstack indico invoiceninja prestashop"
transformations := "dropout summarize restyle add_noise"
rq3_models := "gpt qwen-3b qwen-7b qwen-32b qwen-72b"
rq4_models := "qwen-3b qwen-7b qwen-32b qwen-72b"

# RQ1: run a method on an application's test cases
rq1 method application: \
    (_choose "method" method methods) \
    (_choose "application" application applications) \
    (_evaluate \
        if method == "webtestpilot" { webtestpilot_venv } else { root / "baselines" / method / ".venv" } \
        experiments / "rq1" / "results" / method + "_" + application \
        method application \
        "--test-paths" benchmark / application / "test_cases")

# RQ1: run every method on every application
rq1-all: (_run-all "rq1" methods)

# RQ2: run a method on an application's test cases with bugs injected
rq2 method application: \
    (_choose "method" method assertion_methods) \
    (_choose "application" application applications) \
    (_evaluate \
        if method == "webtestpilot" { webtestpilot_venv } else { root / "baselines" / method / ".venv" } \
        experiments / "rq2" / "results" / method + "_" + application \
        method application \
        "--inject-bug" \
        "--test-paths" benchmark / application / "test_cases" \
        "--bug-paths" benchmark / application / "bugs")

# RQ2: run every assertion-capable method on every application
rq2-all: (_run-all "rq2" assertion_methods)

# RQ3: generate transformed test cases for an application
rq3-transform application: (_choose "application" application applications)
    cd rq3/transform && uv run baml-cli generate && uv run transform.py "$1"

# RQ3: run WebTestPilot on transformed test cases
rq3 model application transformation: \
    (_choose "model" model rq3_models) \
    (_choose "application" application applications) \
    (_choose "transformation" transformation transformations) \
    (_require-transformed application transformation) \
    (_evaluate webtestpilot_venv \
        experiments / "rq3" / "results" / model + "_" + application + "_" + transformation \
        "webtestpilot" application \
        "--method-config-path" experiments / "rq3" / "method_config.yaml" \
        "--test-paths" experiments / "rq3" / "transform" / application / transformation)

# RQ3: run WebTestPilot on transformed test cases with bugs injected
rq3-bug model application transformation: \
    (_choose "model" model rq3_models) \
    (_choose "application" application applications) \
    (_choose "transformation" transformation transformations) \
    (_require-transformed application transformation) \
    (_evaluate webtestpilot_venv \
        experiments / "rq3" / "results" / "bug_" + model + "_" + application + "_" + transformation \
        "webtestpilot" application \
        "--inject-bug" \
        "--method-config-path" experiments / "rq3" / "method_config.bug.yaml" \
        "--test-paths" experiments / "rq3" / "transform" / application / transformation \
        "--bug-paths" benchmark / application / "bugs")

# RQ4: run WebTestPilot with a local model
rq4 model application: \
    (_choose "model" model rq4_models) \
    (_choose "application" application applications) \
    (_evaluate webtestpilot_venv \
        experiments / "rq4" / "results" / model + "_" + application \
        "webtestpilot" application \
        "--method-config-path" experiments / "rq4" / "method_config.yaml" \
        "--test-paths" benchmark / application / "test_cases")

# RQ4: run WebTestPilot with a local model and bugs injected
rq4-bug model application: \
    (_choose "model" model rq4_models) \
    (_choose "application" application applications) \
    (_evaluate webtestpilot_venv \
        experiments / "rq4" / "results" / "bug_" + model + "_" + application \
        "webtestpilot" application \
        "--inject-bug" \
        "--method-config-path" experiments / "rq4" / "method_config.bug.yaml" \
        "--test-paths" benchmark / application / "test_cases" \
        "--bug-paths" benchmark / application / "bugs")

# ============================================
# Helpers
# ============================================

# Fail unless `value` is one of the space-separated `choices`
[private]
_choose name value choices:
    #!/usr/bin/env bash
    if [[ " $3 " != *" $2 "* ]]; then
        echo "❌ Invalid $1: '$2'. Allowed values: $3" >&2
        exit 1
    fi

[private]
_require-transformed application transformation:
    #!/usr/bin/env bash
    if [[ ! -d "rq3/transform/$1/$2" ]]; then
        echo "❌ Transformed test cases not found: experiments/rq3/transform/$1/$2" >&2
        echo "   Generate them first: just run rq3-transform $1" >&2
        exit 1
    fi

# Run `recipe METHOD APPLICATION` for every method and application, continuing past failures
[private]
_run-all recipe methods:
    #!/usr/bin/env bash
    recipe="$1"; methods="$2"; failed=()
    for method in $methods; do
        for application in {{applications}}; do
            echo "▶ just run $recipe $method $application"
            "{{just_executable()}}" --justfile "{{justfile()}}" "{{module_path()}}::$recipe" "$method" "$application" \
                || failed+=("$method $application")
        done
    done
    if (( ${#failed[@]} )); then
        echo "❌ $recipe failed for: $(IFS=,; echo "${failed[*]}")" >&2
        exit 1
    fi
    echo "✅ $recipe completed for all combinations"

# Run baselines.evaluate from the repository root in a virtualenv, logging to the output directory
[private]
_evaluate venv output_dir *args:
    #!/usr/bin/env bash
    set -euo pipefail
    venv="$1"; output_dir="$2"; shift 2
    if [[ ! -f "$venv/bin/activate" ]]; then
        echo "❌ Virtualenv not found: $venv. Run: just setup" >&2
        exit 1
    fi
    source "$venv/bin/activate"
    mkdir -p "$output_dir"
    cd "{{root}}"
    python -u -m baselines.evaluate "$@" --output-dir "$output_dir" \
        2>&1 | tee "$output_dir/run_$(date +%Y%m%d_%H%M%S).log"
    echo
    echo "✅ Evaluation completed successfully"
    echo "📁 Results saved to: $output_dir"
