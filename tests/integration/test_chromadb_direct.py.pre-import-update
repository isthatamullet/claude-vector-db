#!/usr/bin/env python3

from database.vector_database import ClaudeVectorDatabase

# Test direct ChromaDB query without enhancements
db = ClaudeVectorDatabase()
print(f'Collection has {db.collection.count()} entries')

# Test basic ChromaDB query (should always return results)
basic_results = db.collection.query(
    query_texts=['solution implementation'],
    n_results=5,
    include=['documents', 'distances', 'metadatas']
)

print(f'Basic ChromaDB query results: {len(basic_results["documents"][0]) if basic_results["documents"] else 0}')

if basic_results['documents'] and basic_results['documents'][0]:
    print('First result:')
    print(f'  Distance: {basic_results["distances"][0][0]}')
    print(f'  Content preview: {basic_results["documents"][0][0][:100]}...')
    
    # Test the enhanced search method directly
    print('\nTesting enhanced search method:')
    enhanced_results = db.search_conversations_enhanced(
        query='solution implementation',
        n_results=5
    )
    print(f'Enhanced search results: {len(enhanced_results)}')
    
else:
    print('No results from basic ChromaDB query!')
    print(f'Results structure: {basic_results}')