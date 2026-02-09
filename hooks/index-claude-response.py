#!/usr/bin/env python3
"""
Claude Code Stop Hook - UNIFIED PROCESSOR VERSION
Indexes Claude's response(s) using unified enhancement processor
"""

import sys
import json
import time
from pathlib import Path
import re

# Add enhanced vector DB path to Python path (relative to this hook file)
import os

# Calculate path relative to hook location
VECTOR_DB_ROOT = Path(__file__).parent.parent.parent / '.claude-vector-db-enhanced'
sys.path.append(str(VECTOR_DB_ROOT))

try:
    from database.vector_database import ClaudeVectorDatabase
    from processing.enhanced_processor import (
        process_hook_entry,
        normalize_hook_data,
        ProcessingContext
    )
except ImportError as e:
    print(f"Error importing enhanced vector DB modules: {e}", file=sys.stderr)
    sys.exit(1)

def extract_conversation_context(transcript_path: str, session_id: str):
    """Extract conversation context for adjacency-aware processing"""
    
    # Read full transcript for adjacency analysis
    if not Path(transcript_path).exists():
        return [], []
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return [], []
    
    all_messages = []
    recent_responses = []
    
    # Parse all messages for context
    for line in lines:
        if not line.strip():
            continue
        try:
            entry_data = json.loads(line)
            message = entry_data.get('message', {})
            content = message.get('content', '')
            
            # Handle different content formats
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'text':
                            text_parts.append(item.get('text', ''))
                        elif 'content' in item:
                            text_parts.append(str(item['content']))
                    elif isinstance(item, str):
                        text_parts.append(item)
                content = ' '.join(text_parts)
            elif not isinstance(content, str):
                content = str(content)
            
            if content.strip():
                message_data = {
                    'id': f"{session_id}_{entry_data.get('type', 'unknown')}_{len(all_messages)}",
                    'content': content,
                    'type': entry_data.get('type', 'unknown'),
                    'timestamp': entry_data.get('timestamp', time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'),
                    'entry_data': entry_data
                }
                all_messages.append(message_data)
                
                # Collect recent Claude responses for indexing
                if (entry_data.get('type') == 'assistant' and 
                    len([m for m in all_messages if m['type'] == 'assistant']) <= 3):
                    recent_responses.append(message_data)
                    
        except json.JSONDecodeError:
            continue
    
    return all_messages, recent_responses[-3:]  # Return context + recent responses

def index_claude_responses():
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())
        
        # Extract data
        session_id = hook_input.get('session_id', 'unknown')
        transcript_path = hook_input.get('transcript_path', '')
        cwd = hook_input.get('cwd', '/home/user')
        
        # Skip if no transcript path
        if not transcript_path:
            return True
        
        # Log execution with unified processor flag
        log_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')}: [UNIFIED] Indexing Claude responses for session {session_id}\n"
        with open('/home/user/.claude/hooks/logs/response-indexer.log', 'a') as f:
            f.write(log_msg)
        
        # Extract conversation context and new responses
        all_messages, responses = extract_conversation_context(transcript_path, session_id)
        
        if not responses:
            print("No new responses to index")
            return True
        
        # Initialize vector database
        db = ClaudeVectorDatabase()
        
        entries = []
        
        for i, response in enumerate(responses):
            # Find response position in full conversation
            response_position = None
            for pos, msg in enumerate(all_messages):
                if msg['id'] == response['id']:
                    response_position = pos
                    break
            
            # Create hook input data for unified processor
            hook_data = {
                'type': 'assistant',
                'content': response['content'],
                'timestamp': response['timestamp']
            }
            
            # Build processing context with conversation adjacency
            context_messages = all_messages[:response_position] if response_position else []
            
            # Use unified processor to create enhanced entry
            enhanced_entry = process_hook_entry(
                hook_input=hook_data,
                session_id=session_id,
                cwd=cwd,
                previous_messages=context_messages
            )
            
            # Update entry ID to match original response ID if available
            if response.get('id'):
                enhanced_entry.id = response['id']
            
            # Update file name from transcript path
            enhanced_entry.file_name = Path(transcript_path).name
            
            entries.append(enhanced_entry)
        
        # Index entries
        if entries:
            result = db.batch_add_enhanced_entries(entries, batch_size=len(entries))
            print(f"Indexed {len(entries)} Claude responses: {result}")
            
            # Log success with unified processor details
            entry_topics = [list(entry.detected_topics.keys())[:2] for entry in entries]
            success_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')}: [UNIFIED] Successfully indexed {len(entries)} responses (topics: {entry_topics})\n"
            with open('/home/user/.claude/hooks/logs/response-indexer.log', 'a') as f:
                f.write(success_msg)
        
        return True
        
    except Exception as e:
        session_id = locals().get('session_id', 'unknown')
        error_msg = f"{time.strftime('%Y-%m-%d %H:%M:%S')}: [UNIFIED] Error indexing responses for session {session_id}: {e}\n"
        with open('/home/user/.claude/hooks/logs/response-indexer.log', 'a') as f:
            f.write(error_msg)
        print(f"Error indexing responses: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = index_claude_responses()
    sys.exit(0 if success else 1)
