#!/bin/bash

# Check if PR number is provided
if [ -z "$1" ]; then
    echo "Error: PR number is required"
    echo "Usage: $0 <pr-number>"
    exit 1
fi

PR_NUMBER=$1
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="./coder/out/pr-${PR_NUMBER}-review-${TIMESTAMP}.log"

echo "Handling PR #${PR_NUMBER} review comments..."
echo "Output will be saved to: ${OUTPUT_FILE}"

# Call Claude Code CLI in non-interactive mode with JSON output
stdbuf -o0 claude -p "/resolve-pr-comments ${PR_NUMBER}" --max-turns 25 | tee "${OUTPUT_FILE}"

tail -n 10 ${OUTPUT_FILE}