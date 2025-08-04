#!/usr/bin/env python3
"""
Check actual population of conversation chain fields in the database.
"""

from database.vector_database import ClaudeVectorDatabase

def main():
    print('🔍 Querying database for conversation chain field population...')
    db = ClaudeVectorDatabase()

    # Get all entries
    print('📊 Getting all database entries...')
    results = db.collection.get(include=['metadatas'])
    total_entries = len(results['ids'])
    print(f'Total database entries: {total_entries:,}')

    # Count populated previous_message_id fields
    prev_populated = 0
    next_populated = 0
    both_populated = 0
    prev_samples = []
    next_samples = []

    print('🔍 Analyzing conversation chain fields...')
    for i, metadata in enumerate(results['metadatas']):
        if metadata:
            prev_id = metadata.get('previous_message_id')
            next_id = metadata.get('next_message_id')
            
            # Count non-null, non-empty values
            if prev_id and prev_id != 'null' and str(prev_id).strip() and str(prev_id) != 'None':
                prev_populated += 1
                if len(prev_samples) < 5:
                    prev_samples.append(str(prev_id)[:20] + "...")
                    
            if next_id and next_id != 'null' and str(next_id).strip() and str(next_id) != 'None':
                next_populated += 1
                if len(next_samples) < 5:
                    next_samples.append(str(next_id)[:20] + "...")
                    
            if (prev_id and prev_id != 'null' and str(prev_id).strip() and str(prev_id) != 'None') and \
               (next_id and next_id != 'null' and str(next_id).strip() and str(next_id) != 'None'):
                both_populated += 1

    print()
    print('📈 Conversation Chain Field Population Results:')
    print('━' * 60)
    print(f'Total entries:           {total_entries:,}')
    print(f'previous_message_id:     {prev_populated:,} ({prev_populated/total_entries*100:.2f}%)')
    print(f'next_message_id:         {next_populated:,} ({next_populated/total_entries*100:.2f}%)')
    print(f'Both fields populated:   {both_populated:,} ({both_populated/total_entries*100:.2f}%)')
    print('━' * 60)
    
    print()
    print('📋 Sample populated values:')
    if prev_samples:
        print(f'previous_message_id samples: {prev_samples}')
    if next_samples:
        print(f'next_message_id samples: {next_samples}')
    
    # Also check for sessions with backfill_processed=True
    processed_results = db.collection.get(
        where={'backfill_processed': {'$eq': True}},
        include=['metadatas']
    )
    
    processed_count = len(processed_results['ids'])
    print()
    print(f'🔧 Sessions marked as backfill_processed=True: {processed_count}')

if __name__ == "__main__":
    main()