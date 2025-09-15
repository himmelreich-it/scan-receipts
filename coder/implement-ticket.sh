#!/bin/bash

# Check if ticket number is provided
if [ -z "$1" ]; then
    echo "Error: Ticket number is required"
    echo "Usage: $0 <ticket-number>"
    exit 1
fi

TICKET_NUMBER=$1
TIMESTAMP=$(date +%Y%m%d%H%M%S)
OUTPUT_FILE="${TICKET_NUMBER}-${TIMESTAMP}.json"

echo "Implementing ticket #${TICKET_NUMBER}..."
echo "Output will be saved to: ${OUTPUT_FILE}"

# Call Claude Code CLI in non-interactive mode with JSON output
claude -p --max-turns 25 --output-format json --no-interaction "/implement-ticket ${TICKET_NUMBER}" > "${OUTPUT_FILE}"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Successfully implemented ticket #${TICKET_NUMBER}"
    echo "Results saved to: ${OUTPUT_FILE}"
else
    echo "Error: Failed to implement ticket #${TICKET_NUMBER}"
    exit 1
fi