#!/usr/bin/env python3
"""Test the enhanced processor in complete isolation to verify it works correctly"""

from processing.enhanced_processor import UnifiedEnhancementProcessor
from database.enhanced_context import is_solution_attempt

def test_processor_isolation():
    """Test that the enhanced processor correctly generates solution detection"""
    
    print("🔬 Testing Enhanced Processor in Complete Isolation")
    print("=" * 60)
    
    # Initialize processor
    processor = UnifiedEnhancementProcessor(suppress_init_logging=True)
    
    # Test data that should clearly be solutions
    test_entries = [
        {
            'id': 'test_1',
            'content': 'I will fix this by updating the code. Let me use the Edit tool to make the changes.',
            'type': 'assistant',
            'project_path': '/home/user/test',
            'project_name': 'test',
            'timestamp': '2025-08-04T07:00:00Z',
            'session_id': 'test_session',
            'file_name': 'test.jsonl',
            'has_code': True,
            'tools_used': ['Edit']
        },
        {
            'id': 'test_2', 
            'content': 'Let me implement this solution:\n\n```python\ndef fix_function():\n    return "fixed"\n```',
            'type': 'assistant',
            'project_path': '/home/user/test',
            'project_name': 'test',
            'timestamp': '2025-08-04T07:01:00Z',
            'session_id': 'test_session',
            'file_name': 'test.jsonl',
            'has_code': True,
            'tools_used': []
        },
        {
            'id': 'test_3',
            'content': 'Just a regular user message asking a question.',
            'type': 'user',
            'project_path': '/home/user/test',
            'project_name': 'test', 
            'timestamp': '2025-08-04T07:02:00Z',
            'session_id': 'test_session',
            'file_name': 'test.jsonl',
            'has_code': False,
            'tools_used': []
        }
    ]
    
    print(f"📝 Testing {len(test_entries)} entries...")
    
    for i, entry_data in enumerate(test_entries):
        print(f"\n--- Entry {i+1}: {entry_data['id']} ---")
        print(f"Content: {entry_data['content'][:60]}...")
        print(f"Type: {entry_data['type']}")
        
        # Test the function directly first
        direct_result = is_solution_attempt(entry_data['content'])
        print(f"Direct function result: {direct_result}")
        
        # Test through the processor
        enhanced_entry = processor.process_conversation_entry(entry_data)
        processor_result = enhanced_entry.is_solution_attempt
        print(f"Processor result: {processor_result}")
        
        # Check if they match
        if direct_result == processor_result:
            print("✅ CONSISTENT: Function and processor agree")
        else:
            print(f"❌ MISMATCH: Function={direct_result}, Processor={processor_result}")
    
    print(f"\n📊 Processor Statistics:")
    stats = processor.get_processor_stats()
    print(f"  Entries processed: {stats['entries_processed']}")
    print(f"  Solutions identified: {stats['enhancement_breakdown']['solutions_identified']}")
    
    return True

if __name__ == "__main__":
    test_processor_isolation()