#!/usr/bin/env python3
"""Explore ChromaDB internal schema to understand how to do bulk updates"""

import sqlite3
import json

def explore_chromadb_schema():
    """Explore the actual ChromaDB schema"""
    
    conn = sqlite3.connect('./chroma_db/chroma.sqlite3')
    
    # Check all tables
    print("📊 All tables:")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in cursor.fetchall():
        print(f"  - {table[0]}")
    
    # Check embedding_metadata table
    print("\n📋 embedding_metadata structure:")
    cursor = conn.execute("PRAGMA table_info(embedding_metadata)")
    for column in cursor.fetchall():
        print(f"  - {column[1]} ({column[2]})")
    
    # Sample from embedding_metadata
    print("\n📝 Sample embedding_metadata entries:")
    cursor = conn.execute("SELECT * FROM embedding_metadata LIMIT 3")
    for row in cursor.fetchall():
        print(f"  Row: {row}")
    
    # Check if there are documents/metadata stored elsewhere
    print("\n🔍 Checking other potential tables...")
    
    # Try segments table
    cursor = conn.execute("PRAGMA table_info(segments)")
    segment_columns = [col[1] for col in cursor.fetchall()]
    print(f"Segments columns: {segment_columns}")
    
    if 'metadata' in segment_columns:
        cursor = conn.execute("SELECT * FROM segments LIMIT 2")
        for row in cursor.fetchall():
            print(f"  Segment: {row}")
    
    conn.close()

if __name__ == "__main__":
    explore_chromadb_schema()