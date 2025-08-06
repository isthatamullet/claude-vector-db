#!/usr/bin/env python3
"""
Direct database query to check solution attempt field population
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.vector_database import ClaudeVectorDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_solution_fields():
    """Check the actual population of solution-related fields in the database"""
    
    logger.info("🔍 Checking solution attempt fields in database...")
    
    db = ClaudeVectorDatabase()
    
    # Get all entries to check field population
    try:
        all_results = db.collection.get(
            include=['documents', 'metadatas'],
            limit=1000  # Sample first 1000 entries
        )
        
        total_entries = len(all_results['documents'])
        logger.info(f"📊 Analyzing {total_entries} database entries...")
        
        # Count field populations
        field_stats = {
            'is_solution_attempt': {'true': 0, 'false': 0, 'missing': 0},
            'solution_category': {'populated': 0, 'missing': 0, 'values': set()},
            'is_feedback_to_solution': {'true': 0, 'false': 0, 'missing': 0},
            'related_solution_id': {'populated': 0, 'missing': 0},
            'feedback_message_id': {'populated': 0, 'missing': 0}
        }
        
        solution_examples = []
        feedback_examples = []
        
        for i, metadata in enumerate(all_results['metadatas']):
            # Check is_solution_attempt
            is_solution = metadata.get('is_solution_attempt')
            if is_solution is True:
                field_stats['is_solution_attempt']['true'] += 1
                if len(solution_examples) < 3:
                    content_preview = all_results['documents'][i][:100] + "..."
                    solution_examples.append({
                        'content': content_preview,
                        'metadata': {k: v for k, v in metadata.items() if 'solution' in k.lower() or 'category' in k.lower()}
                    })
            elif is_solution is False:
                field_stats['is_solution_attempt']['false'] += 1
            else:
                field_stats['is_solution_attempt']['missing'] += 1
            
            # Check solution_category
            solution_category = metadata.get('solution_category')
            if solution_category:
                field_stats['solution_category']['populated'] += 1
                field_stats['solution_category']['values'].add(solution_category)
            else:
                field_stats['solution_category']['missing'] += 1
            
            # Check is_feedback_to_solution  
            is_feedback = metadata.get('is_feedback_to_solution')
            if is_feedback is True:
                field_stats['is_feedback_to_solution']['true'] += 1
                if len(feedback_examples) < 3:
                    content_preview = all_results['documents'][i][:100] + "..."
                    feedback_examples.append({
                        'content': content_preview,
                        'metadata': {k: v for k, v in metadata.items() if 'feedback' in k.lower() or 'related' in k.lower()}
                    })
            elif is_feedback is False:
                field_stats['is_feedback_to_solution']['false'] += 1
            else:
                field_stats['is_feedback_to_solution']['missing'] += 1
            
            # Check related_solution_id
            related_solution = metadata.get('related_solution_id')
            if related_solution:
                field_stats['related_solution_id']['populated'] += 1
            else:
                field_stats['related_solution_id']['missing'] += 1
            
            # Check feedback_message_id
            feedback_msg = metadata.get('feedback_message_id')
            if feedback_msg:
                field_stats['feedback_message_id']['populated'] += 1
            else:
                field_stats['feedback_message_id']['missing'] += 1
        
        # Print results
        logger.info("\n" + "="*60)
        logger.info("📊 SOLUTION FIELDS ANALYSIS RESULTS")
        logger.info("="*60)
        
        for field_name, stats in field_stats.items():
            logger.info(f"\n🔍 {field_name}:")
            if 'true' in stats:
                total_bool = stats['true'] + stats['false'] + stats['missing']
                true_pct = (stats['true'] / total_bool * 100) if total_bool > 0 else 0
                false_pct = (stats['false'] / total_bool * 100) if total_bool > 0 else 0
                missing_pct = (stats['missing'] / total_bool * 100) if total_bool > 0 else 0
                logger.info(f"  ✅ True: {stats['true']} ({true_pct:.1f}%)")
                logger.info(f"  ❌ False: {stats['false']} ({false_pct:.1f}%)")
                logger.info(f"  ❓ Missing: {stats['missing']} ({missing_pct:.1f}%)")
            else:
                populated_pct = (stats['populated'] / total_entries * 100) if total_entries > 0 else 0
                missing_pct = (stats['missing'] / total_entries * 100) if total_entries > 0 else 0
                logger.info(f"  ✅ Populated: {stats['populated']} ({populated_pct:.1f}%)")
                logger.info(f"  ❓ Missing: {stats['missing']} ({missing_pct:.1f}%)")
                if 'values' in stats and stats['values']:
                    logger.info(f"  📝 Values: {sorted(list(stats['values']))}")
        
        # Show examples
        if solution_examples:
            logger.info(f"\n🎯 SOLUTION ATTEMPT EXAMPLES ({len(solution_examples)} found):")
            for i, example in enumerate(solution_examples, 1):
                logger.info(f"\nExample {i}:")
                logger.info(f"  Content: {example['content']}")
                logger.info(f"  Metadata: {example['metadata']}")
        
        if feedback_examples:
            logger.info(f"\n💬 FEEDBACK EXAMPLES ({len(feedback_examples)} found):")
            for i, example in enumerate(feedback_examples, 1):
                logger.info(f"\nExample {i}:")
                logger.info(f"  Content: {example['content']}")
                logger.info(f"  Metadata: {example['metadata']}")
        
        logger.info("\n" + "="*60)
        
        # Final assessment
        solutions_found = field_stats['is_solution_attempt']['true']
        feedback_found = field_stats['is_feedback_to_solution']['true']
        
        if solutions_found > 0:
            logger.info(f"✅ SUCCESS: Found {solutions_found} solution attempts!")
            logger.info("   The analyze_solution_feedback_patterns tool should work.")
        else:
            logger.info("❌ PROBLEM: No solution attempts found (is_solution_attempt=True)")
            logger.info("   This explains why analyze_solution_feedback_patterns returns 0 patterns.")
        
        if feedback_found > 0:
            logger.info(f"✅ Found {feedback_found} feedback messages")
        else:
            logger.info("⚠️ No feedback messages found (is_feedback_to_solution=True)")
        
        return {
            'total_entries': total_entries,
            'solution_attempts': solutions_found,
            'feedback_messages': feedback_found,
            'field_stats': field_stats
        }
        
    except Exception as e:
        logger.error(f"❌ Error querying database: {e}")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starting solution fields analysis...")
    results = check_solution_fields()
    
    if results:
        logger.info(f"\n🏁 Analysis complete: {results['solution_attempts']} solutions, {results['feedback_messages']} feedback")
    else:
        logger.info("🏁 Analysis failed")