#!/bin/bash


# Function to run a script and check its output for errors
run_script() {
    script=$1
    output=$(./$script)  # Execute the script and capture its output

    # Check the output for error condition (e.g., keyword "error")
    if echo "$output" | grep -qi "error"; then
        echo "Error detected in script: $script"
        echo "Script output:"
        echo "$output"
    else
        echo "Script '$script' executed successfully."
    fi
}

SCRIPT_DIR=$(dirname "$(realpath "$0")")

echo "Running black to format code..."
run_script "$SCRIPT_DIR/format_code_black.sh"

echo "Running pylint..."
run_script "$SCRIPT_DIR/check_quality_pylint.sh"

echo "Running flake8..."
run_script "$SCRIPT_DIR/check_quality_flake8.sh"

echo "Running ruff..."
run_script "$SCRIPT_DIR/check_quality_ruff.sh"

echo "Running tests..."
run_script "$SCRIPT_DIR/run_tests.sh"

echo "Running coverage percentage..."
run_script "$SCRIPT_DIR/check_test_coverage.sh"

echo "Running bandit..."
run_script "$SCRIPT_DIR/check_quality_bandit.sh"

echo "Running radon..."
run_script "$SCRIPT_DIR/check_quality_radon.sh"

echo "All scripts have been executed."
