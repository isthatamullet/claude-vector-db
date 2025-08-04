#!/usr/bin/env python3

from vector_database import ClaudeVectorDatabase

def analyze_enhanced_metadata():
    db = ClaudeVectorDatabase()
    
    print('=== COMPREHENSIVE ENHANCED METADATA ANALYSIS ===')
    
    enhanced_fields = [
        'detected_topics', 'solution_quality_score', 'validation_strength',
        'is_validated_solution', 'is_refuted_attempt', 'is_solution_attempt', 
        'primary_topic', 'topic_confidence', 'solution_category',
        'user_feedback_sentiment', 'has_quality_indicators', 'has_success_markers',
        'message_sequence_position', 'outcome_certainty', 'is_feedback_to_solution',
        'related_solution_id', 'feedback_message_id', 'next_message_id', 'previous_message_id'
    ]
    
    batch_size = 1000
    total_records = db.collection.count()
    print(f'Total records: {total_records}')
    
    field_stats = {}
    for field in enhanced_fields:
        field_stats[field] = {'has_field': 0, 'populated': 0}
    
    records_with_all_fields = 0
    
    for offset in range(0, total_records, batch_size):
        limit = min(batch_size, total_records - offset)
        results = db.collection.get(limit=limit, offset=offset, include=['metadatas'])
        
        for metadata in results['metadatas']:
            has_all_fields = True
            
            for field in enhanced_fields:
                if field in metadata:
                    field_stats[field]['has_field'] += 1
                    
                    value = metadata[field]
                    is_populated = False
                    
                    if field == 'detected_topics':
                        is_populated = value and value not in ['{}', '', 'null']
                    elif field in ['primary_topic', 'solution_category', 'user_feedback_sentiment', 
                                  'related_solution_id', 'feedback_message_id', 'next_message_id', 'previous_message_id']:  
                        is_populated = value and value not in ['', 'null']
                    elif field in ['solution_quality_score', 'validation_strength', 'topic_confidence', 'outcome_certainty']:
                        is_populated = value != 0 and value != 0.0
                    elif field == 'message_sequence_position':
                        is_populated = value != 0
                    elif field in ['is_validated_solution', 'is_refuted_attempt', 'is_solution_attempt',
                                  'has_quality_indicators', 'has_success_markers', 'is_feedback_to_solution']:
                        is_populated = value is True
                    
                    if is_populated:
                        field_stats[field]['populated'] += 1
                else:
                    has_all_fields = False
            
            if has_all_fields:
                records_with_all_fields += 1
        
        if offset % 5000 == 0:
            print(f'Processed {offset + limit}/{total_records}...')
    
    print()
    print('=== RESULTS ===')
    print(f'Records with ALL enhanced fields: {records_with_all_fields} ({(records_with_all_fields/total_records)*100:.2f}%)')
    print()
    
    sorted_fields = sorted(enhanced_fields, key=lambda f: field_stats[f]['has_field'], reverse=True)
    
    for field in sorted_fields:
        stats = field_stats[field]
        has_pct = (stats['has_field']/total_records)*100
        pop_pct = (stats['populated']/total_records)*100
        pop_of_has = (stats['populated']/stats['has_field'])*100 if stats['has_field'] > 0 else 0
        
        print(f'{field:25} | Has: {stats["has_field"]:5} ({has_pct:5.2f}%) | Pop: {stats["populated"]:5} ({pop_pct:5.2f}%) | {pop_of_has:5.1f}% of field holders')
    
    print()
    high_coverage = sum(1 for f in enhanced_fields if field_stats[f]['has_field'] > total_records * 0.99)
    meaningful_data = sum(1 for f in enhanced_fields if field_stats[f]['populated'] > total_records * 0.01)
    print(f'Fields with 99%+ coverage: {high_coverage}/{len(enhanced_fields)}')
    print(f'Fields with 1%+ populated: {meaningful_data}/{len(enhanced_fields)}')

if __name__ == '__main__':
    analyze_enhanced_metadata()