#!/bin/bash

# Check if ticket number is provided
if [ -z "$1" ]; then
    echo "Error: Ticket number is required"
    echo "Usage: $0 <ticket-number>"
    exit 1
fi

TICKET_NUMBER=$1
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="./coder/out/${TICKET_NUMBER}-${TIMESTAMP}.log"

echo "Implementing ticket #${TICKET_NUMBER}..."
echo "Output will be saved to: ${OUTPUT_FILE}"

# Call Claude Code CLI in non-interactive mode with JSON output
stdbuf -o0 claude -p "/implement-ticket ${TICKET_NUMBER}" --max-turns 25 | tee "${OUTPUT_FILE}"

tail -n 10 ${OUTPUT_FILE}