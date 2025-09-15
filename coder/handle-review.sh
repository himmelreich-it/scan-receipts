#!/bin/bash

# Check if PR number is provided
if [ -z "$1" ]; then
    echo "Error: PR number is required"
    echo "Usage: $0 <pr-number>"
    exit 1
fi

PR_NUMBER=$1
TIMESTAMP=$(date +%Y%m%d%H%M%S)
OUTPUT_FILE="pr-${PR_NUMBER}-review-${TIMESTAMP}.json"

echo "Handling PR #${PR_NUMBER} review comments..."
echo "Output will be saved to: ${OUTPUT_FILE}"

# Call Claude Code CLI in non-interactive mode with JSON output
claude -p --max-turns 25 --output-format json --no-interaction "/resolve-pr-comments ${PR_NUMBER}" > "${OUTPUT_FILE}"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Successfully handled PR #${PR_NUMBER} review comments"
    echo "Results saved to: ${OUTPUT_FILE}"
else
    echo "Error: Failed to handle PR #${PR_NUMBER} review comments"
    exit 1
fi