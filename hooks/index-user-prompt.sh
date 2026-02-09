#!/bin/bash
#
# Claude Code UserPromptSubmit Hook
# Indexes user prompts into vector database and provides current date/time to Claude
#

# Call Python script to handle the actual indexing first
cd /home/user/.claude-vector-db-enhanced
./venv/bin/python /home/user/.claude/hooks/index-user-prompt.py

# Save the exit code
PYTHON_EXIT_CODE=$?

# Then inject current date and time for Claude with Denver timezone info
echo "Current time: $(date -u '+Today is %B %d, %Y, %l:%M %p UTC') | User timezone: America/Denver"

# Exit with the Python script's code
exit $PYTHON_EXIT_CODE
