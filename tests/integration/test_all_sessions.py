#!/usr/bin/env python3
"""
Test script to process all sessions with conversation chain back-fill.
"""

from processing.conversation_backfill_engine import ConversationBackFillEngine
from database.vector_database import ClaudeVectorDatabase
import time

def main():
    print("🔗 Testing Conversation Chain Back-Fill on All Sessions")
    print("=" * 60)
    
    # Initialize components
    db = ClaudeVectorDatabase()
    engine = ConversationBackFillEngine(db)
    
    # Get all sessions in database
    print("\n📋 Getting all sessions from database...")
    results = db.collection.get(include=['metadatas'])
    all_sessions = set()
    for metadata in results.get('metadatas', []):
        if metadata and metadata.get('session_id'):
            all_sessions.add(metadata['session_id'])
    
    session_list = list(all_sessions)
    print(f"Found {len(session_list)} unique sessions")
    
    # Get already processed sessions to avoid reprocessing
    print(f"\n🔍 Checking for already processed sessions...")
    processed_results = db.collection.get(
        where={'backfill_processed': {'$eq': True}},
        include=['metadatas']
    )
    
    processed_sessions = set()
    for metadata in processed_results.get('metadatas', []):
        if metadata and metadata.get('session_id'):
            processed_sessions.add(metadata['session_id'])
    
    print(f"Already processed sessions: {len(processed_sessions)}")
    
    # Process only remaining sessions
    remaining_sessions = [s for s in session_list if s not in processed_sessions]
    test_sessions = remaining_sessions
    print(f"\n⚙️ Processing {len(test_sessions)} remaining sessions...")
    
    successful = 0
    total_relationships = 0
    total_updates = 0
    start_time = time.time()
    
    for i, session_id in enumerate(test_sessions):
        print(f"\n📋 Processing session {i+1}/{len(test_sessions)}: {session_id[:8]}...")
        
        try:
            result = engine.process_session(session_id)
            
            if result.success:
                successful += 1
                total_relationships += result.relationships_built
                total_updates += result.database_updates
                print(f"   ✅ Success: {result.relationships_built} relationships, {result.database_updates} updates")
            else:
                print(f"   ❌ Failed: {result.error_count} errors")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    elapsed = time.time() - start_time
    print(f"\n📊 Results:")
    print(f"   Successful sessions: {successful}/{len(test_sessions)}")
    print(f"   Total relationships built: {total_relationships}")
    print(f"   Total database updates: {total_updates}")
    print(f"   Processing time: {elapsed:.1f} seconds")
    print(f"   Average time per session: {elapsed/len(test_sessions):.1f} seconds")
    
    # Check final processed sessions count
    print(f"\n🔍 Checking final processed sessions count...")
    final_processed_results = db.collection.get(
        where={'backfill_processed': {'$eq': True}},
        include=['metadatas']
    )
    
    final_processed_sessions = set()
    for metadata in final_processed_results.get('metadatas', []):
        if metadata and metadata.get('session_id'):
            final_processed_sessions.add(metadata['session_id'])
    
    print(f"Total sessions now processed: {len(final_processed_sessions)}/{len(session_list)}")
    print(f"Sessions remaining: {len(session_list) - len(final_processed_sessions)}")
    
    # Analyze conversation chain coverage after processing
    print(f"\n📈 Analyzing conversation chain coverage...")
    coverage_analysis = engine.analyze_conversation_chain_coverage()
    
    if 'error' not in coverage_analysis:
        overall_health = coverage_analysis.get('overall_chain_health', 0)
        print(f"   Overall chain health: {overall_health:.1f}%")
        print(f"   Target coverage: {coverage_analysis.get('target_coverage', 80)}%")
        print(f"   Meets target: {'✅' if coverage_analysis.get('meets_target') else '❌'}")
        
        key_fields = ['previous_message_id', 'next_message_id']
        for field in key_fields:
            if field in coverage_analysis.get('field_coverage', {}):
                stats = coverage_analysis['field_coverage'][field]
                coverage = stats['coverage_percentage']
                print(f"   • {field}: {coverage:.1f}% ({stats['populated']}/{stats['total']})")
    
    print(f"\n✅ Test completed!")

if __name__ == "__main__":
    main()