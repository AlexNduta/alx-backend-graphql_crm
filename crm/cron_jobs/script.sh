#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../../"  # Move to project root from crm/cron_jobs/
# Activate virtual environment if needed
# source /path/to/venv/bin/activate 
echo "Running script from: $SCRIPT_DIR"