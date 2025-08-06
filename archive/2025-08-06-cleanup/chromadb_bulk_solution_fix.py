#!/usr/bin/env python3
"""
Efficient ChromaDB solution detection fix using ChromaDB API
Instead of direct SQLite access, use ChromaDB's API for bulk operations
"""

from database.vector_database import ClaudeVectorDatabase
from database.enhanced_context import is_solution_attempt

def efficient_solution_detection_fix():
    """Fix solution detection efficiently using ChromaDB API with batching"""
    
    print("🔧 Efficient solution detection fix using ChromaDB API...")
    
    db = ClaudeVectorDatabase()
    
    # Get all entries that currently have is_solution_attempt = False
    print("🔍 Querying entries marked as non-solutions...")
    
    results = db.collection.get(
        where={"is_solution_attempt": False},  # Only False entries
        include=['documents', 'metadatas']  # ids are included by default
    )
    
    print(f"📊 Found {len(results['ids'])} entries marked as False")
    
    if not results['ids']:
        print("✅ No entries to update!")
        return
    
    # Process in batches to check which should actually be True
    batch_size = 1000
    total_updates = 0
    
    for i in range(0, len(results['ids']), batch_size):
        print(f"\n📦 Processing batch {i//batch_size + 1}...")
        
        batch_ids = results['ids'][i:i+batch_size]
        batch_docs = results['documents'][i:i+batch_size]
        batch_metadata = results['metadatas'][i:i+batch_size]
        
        # Find entries that should be True
        updates_needed = []
        update_ids = []
        update_metadata = []
        
        for j, (doc, metadata, entry_id) in enumerate(zip(batch_docs, batch_metadata, batch_ids)):
            if is_solution_attempt(doc):
                # This should be True, not False
                updated_metadata = metadata.copy()
                updated_metadata['is_solution_attempt'] = True
                
                update_ids.append(entry_id)
                update_metadata.append(updated_metadata)
                updates_needed.append(j)
                
                # Show sample
                if len(updates_needed) <= 5:
                    print(f"  ✅ Should be True: {doc[:60]}...")
        
        # Bulk update this batch
        if update_ids:
            try:
                db.collection.update(
                    ids=update_ids,
                    metadatas=update_metadata
                )
                total_updates += len(update_ids)
                print(f"  💾 Updated {len(update_ids)} entries in this batch")
            except Exception as e:
                print(f"  ❌ Error updating batch: {e}")
        else:
            print("  ℹ️ No updates needed in this batch")
    
    print(f"\n🎯 Bulk update complete!")
    print(f"✅ Total entries updated: {total_updates}")
    
    # Verify results
    print("\n📊 Verification...")
    solution_results = db.collection.get(
        where={"is_solution_attempt": True}
    )
    print(f"Total solutions now: {len(solution_results['ids'])}")
    
    return total_updates

if __name__ == "__main__":
    efficient_solution_detection_fix()