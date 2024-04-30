#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")

TESTS_DIR="$SCRIPT_DIR/../tests"

export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/../

pytest $TEST_DIR

