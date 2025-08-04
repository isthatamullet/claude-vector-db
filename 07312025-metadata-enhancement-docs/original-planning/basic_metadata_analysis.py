#!/usr/bin/env python3

from vector_database import ClaudeVectorDatabase

def analyze_basic_metadata():
    db = ClaudeVectorDatabase()
    
    print('=== BASIC METADATA FIELD ANALYSIS ===')
    
    # Define enhanced metadata fields (from our previous analysis)
    enhanced_fields = {
        'detected_topics', 'solution_quality_score', 'validation_strength',
        'is_validated_solution', 'is_refuted_attempt', 'is_solution_attempt', 
        'primary_topic', 'topic_confidence', 'solution_category',
        'user_feedback_sentiment', 'has_quality_indicators', 'has_success_markers',
        'message_sequence_position', 'outcome_certainty', 'is_feedback_to_solution',
        'related_solution_id', 'feedback_message_id', 'next_message_id', 'previous_message_id'
    }
    
    # Define basic metadata fields (everything else)
    basic_fields = [
        'content_hash', 'content_length', 'file_name', 'has_code', 
        'project_name', 'project_path', 'session_id', 'timestamp', 
        'timestamp_unix', 'tools_used', 'type'
    ]
    
    batch_size = 1000
    total_records = db.collection.count()
    print(f'Total records: {total_records}')
    
    field_stats = {}
    for field in basic_fields:
        field_stats[field] = {'has_field': 0, 'populated': 0, 'sample_values': set()}
    
    records_with_all_basic_fields = 0
    
    for offset in range(0, total_records, batch_size):
        limit = min(batch_size, total_records - offset)
        results = db.collection.get(limit=limit, offset=offset, include=['metadatas'])
        
        for metadata in results['metadatas']:
            has_all_basic = True
            
            for field in basic_fields:
                if field in metadata:
                    field_stats[field]['has_field'] += 1
                    
                    value = metadata[field]
                    is_populated = False
                    
                    if field in ['content_hash', 'file_name', 'project_name', 'project_path', 'session_id', 'timestamp', 'type']:
                        # String fields - populated if not empty
                        is_populated = value and value not in ['', 'null', None]
                    elif field in ['content_length', 'timestamp_unix']:
                        # Numeric fields - populated if not zero
                        is_populated = value != 0 and value != 0.0
                    elif field == 'has_code':
                        # Boolean field - always populated (True/False both valid)
                        is_populated = isinstance(value, bool)
                    elif field == 'tools_used':
                        # JSON string field - populated if not empty array
                        is_populated = value and value not in ['[]', '', 'null']
                    
                    if is_populated:
                        field_stats[field]['populated'] += 1
                        # Keep sample values (limit to 5 unique samples)
                        if len(field_stats[field]['sample_values']) < 5:
                            if isinstance(value, str) and len(value) > 50:
                                field_stats[field]['sample_values'].add(value[:50] + '...')
                            else:
                                field_stats[field]['sample_values'].add(str(value))
                else:
                    has_all_basic = False
            
            if has_all_basic:
                records_with_all_basic_fields += 1
        
        if offset % 5000 == 0:
            print(f'Processed {offset + limit}/{total_records}...')
    
    print()
    print('=== RESULTS ===')
    print(f'Records with ALL basic fields: {records_with_all_basic_fields} ({(records_with_all_basic_fields/total_records)*100:.2f}%)')
    print()
    
    sorted_fields = sorted(basic_fields, key=lambda f: field_stats[f]['has_field'], reverse=True)
    
    for field in sorted_fields:
        stats = field_stats[field]
        has_pct = (stats['has_field']/total_records)*100
        pop_pct = (stats['populated']/total_records)*100
        pop_of_has = (stats['populated']/stats['has_field'])*100 if stats['has_field'] > 0 else 0
        
        print(f'{field:25} | Has: {stats["has_field"]:5} ({has_pct:5.2f}%) | Pop: {stats["populated"]:5} ({pop_pct:5.2f}%) | {pop_of_has:5.1f}% of field holders')
        
        # Show sample values for context
        if stats['sample_values']:
            samples = ', '.join(list(stats['sample_values'])[:3])
            print(f'{"":25} | Samples: {samples}')
        print()
    
    print()
    high_coverage = sum(1 for f in basic_fields if field_stats[f]['has_field'] > total_records * 0.99)
    meaningful_data = sum(1 for f in basic_fields if field_stats[f]['populated'] > total_records * 0.01)
    
    print(f'Basic fields with 99%+ coverage: {high_coverage}/{len(basic_fields)}')
    print(f'Basic fields with 1%+ populated: {meaningful_data}/{len(basic_fields)}')

if __name__ == '__main__':
    analyze_basic_metadata()