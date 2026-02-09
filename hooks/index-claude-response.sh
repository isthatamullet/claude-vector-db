#!/bin/bash
#
# Claude Code Stop Hook - Response Indexer Component
# Indexes Claude's responses directly into vector database in real-time
#

# Call Python script to handle the actual indexing
cd /home/user/.claude-vector-db-enhanced
./venv/bin/python /home/user/.claude/hooks/index-claude-response.py

# Exit with the same code as Python script
exit $?
