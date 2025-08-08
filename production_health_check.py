#!/usr/bin/env python3
"""Comprehensive production health check for hybrid system"""

import sys
import traceback
sys.path.insert(0, '.')

from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor
from processing.hybrid_spacy_st_processor import HybridSpacySTProcessor

def run_production_health_check():
    """Run comprehensive health check for hybrid system"""
    
    print("🏥 Running Production Health Check")
    print("=" * 50)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Database connectivity
    checks_total += 1
    print("\n1. Database Connectivity...")
    try:
        db = ClaudeVectorDatabase()
        count = db.collection.count()
        print(f"   ✅ Database connected: {count} entries")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
    
    # Check 2: Hybrid processor initialization
    checks_total += 1
    print("\n2. Hybrid Processor Initialization...")
    try:
        processor = HybridSpacySTProcessor()
        stats = processor.get_processor_stats()
        print(f"   ✅ Hybrid processor status: {stats['status']}")
        checks_passed += 1
    except Exception as e:
        print(f"   ❌ Hybrid processor failed: {e}")
    
    # Check 3: Enhancement processor integration
    checks_total += 1
    print("\n3. Enhancement Processor Integration...")
    try:
        unified_processor = UnifiedEnhancementProcessor(
            enable_hybrid=True,
            suppress_init_logging=True
        )
        stats = unified_processor.get_processor_stats()
        component_count = stats.get('components_available', 0)
        
        if component_count >= 8:
            print(f"   ✅ All components active: {component_count}/8")
            checks_passed += 1
        else:
            print(f"   ⚠️ Missing components: {component_count}/8")
    except Exception as e:
        print(f"   ❌ Enhancement processor failed: {e}")
    
    # Check 4: Search performance
    checks_total += 1
    print("\n4. Search Performance...")
    try:
        db = ClaudeVectorDatabase()
        import time
        
        start_time = time.time()
        results = db.search_conversations("test performance", n_results=5)
        search_time = (time.time() - start_time) * 1000
        
        if search_time < 200:
            print(f"   ✅ Search performance good: {search_time:.1f}ms")
            checks_passed += 1
        else:
            print(f"   ⚠️ Search performance slow: {search_time:.1f}ms")
    except Exception as e:
        print(f"   ❌ Search performance test failed: {e}")
    
    # Check 5: Hybrid extraction functionality
    checks_total += 1
    print("\n5. Hybrid Extraction Functionality...")
    try:
        processor = HybridSpacySTProcessor()
        test_content = "I used the Edit tool to fix React component errors in TypeScript"
        
        results = processor.extract_intelligence(test_content)
        confidence = results.get('hybrid_confidence', 0.0)
        
        if confidence > 0:
            print(f"   ✅ Hybrid extraction working: {confidence:.3f} confidence")
            checks_passed += 1
        else:
            print(f"   ⚠️ Hybrid extraction low confidence: {confidence:.3f}")
    except Exception as e:
        print(f"   ❌ Hybrid extraction failed: {e}")
    
    # Check 6: MCP server readiness
    checks_total += 1
    print("\n6. MCP Server Readiness...")
    try:
        # Test MCP server file exists and has basic structure
        with open('mcp/mcp_server.py', 'r') as f:
            content = f.read()
            if 'search_conversations_unified' in content:
                print("   ✅ MCP server file ready with hybrid tools")
                checks_passed += 1
            else:
                print("   ⚠️ MCP server missing hybrid tools")
    except Exception as e:
        print(f"   ❌ MCP server readiness check failed: {e}")
    
    # Final assessment
    print("\n" + "=" * 50)
    print(f"Health Check Results: {checks_passed}/{checks_total} passed")
    
    if checks_passed == checks_total:
        print("🎉 All health checks passed - System ready for production!")
        return True
    elif checks_passed >= checks_total * 0.8:  # 80% threshold
        print("⚠️ Most health checks passed - System functional with warnings")
        return True
    else:
        print("❌ Critical health check failures - System needs attention")
        return False

if __name__ == "__main__":
    success = run_production_health_check()
    if not success:
        sys.exit(1)