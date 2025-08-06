#!/usr/bin/env python3
"""
Quick solution detection fix via direct ChromaDB SQLite access
Bypasses the slow individual processing and updates metadata directly
"""

import sqlite3
import json
import re
from database.enhanced_context import is_solution_attempt

def quick_fix_solution_detection():
    """Fix solution detection via direct SQLite access to ChromaDB"""
    
    print("🔧 Quick solution detection fix via ChromaDB SQLite...")
    
    # Connect to ChromaDB's internal SQLite database
    db_path = './chroma_db/chroma.sqlite3'
    conn = sqlite3.connect(db_path)
    
    try:
        # First, let's see the structure
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Found tables: {tables}")
        
        # Check the embeddings table structure
        cursor = conn.execute("PRAGMA table_info(embeddings)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Embeddings columns: {columns}")
        
        # Get total count
        cursor = conn.execute("SELECT COUNT(*) FROM embeddings")
        total_count = cursor.fetchone()[0]
        print(f"📈 Total entries: {total_count}")
        
        # Find entries that should be solutions but aren't marked
        print("\n🔍 Finding entries that should be solutions...")
        
        # Query entries with solution-like content
        cursor = conn.execute("""
            SELECT id, document, metadata 
            FROM embeddings 
            WHERE (document LIKE '%let me implement%' 
                OR document LIKE '%I''ll fix%'
                OR document LIKE '%```%python%'
                OR document LIKE '%```typescript%'
                OR document LIKE '%```javascript%'
                OR document LIKE '%multiedit%'
                OR document LIKE '%edit tool%')
            AND json_extract(metadata, '$.is_solution_attempt') = 'false'
            LIMIT 100
        """)
        
        candidates = cursor.fetchall()
        print(f"📝 Found {len(candidates)} candidate entries to check")
        
        # Process candidates with our solution detection function
        updates_needed = []
        for entry_id, document, metadata_json in candidates:
            if is_solution_attempt(document):
                # Parse metadata and update
                metadata = json.loads(metadata_json) if metadata_json else {}
                metadata['is_solution_attempt'] = True
                updates_needed.append((entry_id, json.dumps(metadata)))
                
                print(f"  ✅ Entry {entry_id}: {document[:50]}...")
        
        print(f"\n🔄 Updating {len(updates_needed)} entries...")
        
        # Bulk update in SQLite
        if updates_needed:
            conn.executemany("""
                UPDATE embeddings 
                SET metadata = ? 
                WHERE id = ?
            """, [(metadata, entry_id) for entry_id, metadata in updates_needed])
            
            conn.commit()
            print(f"✅ Updated {len(updates_needed)} entries successfully!")
        else:
            print("ℹ️ No updates needed")
            
        # Verify the changes
        cursor = conn.execute("""
            SELECT COUNT(*) FROM embeddings 
            WHERE json_extract(metadata, '$.is_solution_attempt') = 'true'
        """)
        solution_count = cursor.fetchone()[0]
        print(f"📊 Total solutions now: {solution_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n🎯 Quick fix complete! Solution detection updated via direct SQLite access.")

if __name__ == "__main__":
    quick_fix_solution_detection()