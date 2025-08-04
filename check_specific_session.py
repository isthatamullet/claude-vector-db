#!/usr/bin/env python3
"""
Check the specific session that was updated in the selective field reprocessing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.vector_database import ClaudeVectorDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_specific_session():
    """Check the specific session that was supposedly updated"""
    
    session_id = "f8a4b940-4909-44f7-9196-4ed1342872dc"
    logger.info(f"🔍 Checking specific session: {session_id}")
    
    db = ClaudeVectorDatabase()
    
    try:
        # Query the specific session that was updated
        session_results = db.collection.get(
            where={"session_id": {"$eq": session_id}},
            include=['documents', 'metadatas'],
            limit=50
        )
        
        total_in_session = len(session_results['documents'])
        logger.info(f"📊 Found {total_in_session} entries in session {session_id}")
        
        if total_in_session == 0:
            logger.warning("❌ Session not found in database!")
            return
        
        # Count solution fields in this specific session
        solution_attempts = 0
        feedback_messages = 0
        solution_categories = set()
        
        logger.info("\n🔍 ANALYZING SESSION ENTRIES:")
        for i, metadata in enumerate(session_results['metadatas']):
            entry_id = session_results['ids'][i] if i < len(session_results['ids']) else f"entry_{i}"
            content_preview = session_results['documents'][i][:80] + "..." if len(session_results['documents'][i]) > 80 else session_results['documents'][i]
            
            is_solution = metadata.get('is_solution_attempt', False)
            is_feedback = metadata.get('is_feedback_to_solution', False)
            solution_category = metadata.get('solution_category')
            
            logger.info(f"\nEntry {i+1} ({entry_id}):")
            logger.info(f"  is_solution_attempt: {is_solution}")
            logger.info(f"  is_feedback_to_solution: {is_feedback}")
            logger.info(f"  solution_category: {solution_category}")
            logger.info(f"  content: {content_preview}")
            
            if is_solution:
                solution_attempts += 1
            if is_feedback:
                feedback_messages += 1
            if solution_category:
                solution_categories.add(solution_category)
        
        logger.info(f"\n📊 SESSION SUMMARY:")
        logger.info(f"  Total entries: {total_in_session}")
        logger.info(f"  Solution attempts: {solution_attempts}")
        logger.info(f"  Feedback messages: {feedback_messages}")
        logger.info(f"  Solution categories: {sorted(list(solution_categories))}")
        
        # Now let's also check the broader database for ALL solution attempts
        logger.info(f"\n🌍 CHECKING ENTIRE DATABASE FOR SOLUTION ATTEMPTS...")
        
        all_solutions = db.collection.get(
            where={'is_solution_attempt': {'$eq': True}},
            include=['documents', 'metadatas'],
            limit=100
        )
        
        total_solutions = len(all_solutions['documents'])
        logger.info(f"📊 Found {total_solutions} total solution attempts in entire database")
        
        if total_solutions > 0:
            logger.info(f"\n🎯 FIRST FEW SOLUTION ATTEMPTS:")
            for i in range(min(5, total_solutions)):
                metadata = all_solutions['metadatas'][i]
                content_preview = all_solutions['documents'][i][:80] + "..." if len(all_solutions['documents'][i]) > 80 else all_solutions['documents'][i]
                session = metadata.get('session_id', 'unknown')
                category = metadata.get('solution_category', 'none')
                
                logger.info(f"\nSolution {i+1}:")
                logger.info(f"  Session: {session}")
                logger.info(f"  Category: {category}")
                logger.info(f"  Content: {content_preview}")
        
        return {
            'session_entries': total_in_session,
            'session_solutions': solution_attempts,
            'session_feedback': feedback_messages,
            'total_database_solutions': total_solutions
        }
        
    except Exception as e:
        logger.error(f"❌ Error querying session: {e}")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starting specific session analysis...")
    results = check_specific_session()
    
    if results:
        logger.info(f"\n🏁 Analysis complete:")
        logger.info(f"   Session solutions: {results['session_solutions']}/{results['session_entries']}")
        logger.info(f"   Total DB solutions: {results['total_database_solutions']}")
        
        if results['total_database_solutions'] > 0:
            logger.info("✅ Database has solution attempts - MCP tool should work!")
        else:
            logger.info("❌ No solution attempts found - this explains the MCP tool issue")
    else:
        logger.info("🏁 Analysis failed")