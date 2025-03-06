#!/bin/bash

# Store the current directory
CURRENT_DIR=$(pwd)
# Resolve the script directory, following symlinks
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Run the script with all provided arguments
python "$SCRIPT_DIR/git_commit_generator.py" "$@"

# Return value
RETURN_VALUE=$?

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

# Return to the original directory
cd "$CURRENT_DIR"

# Exit with the return value of the python script
exit $RETURN_VALUE
