#!/usr/bin/env python3
"""Comprehensive system validation for hybrid enhancement"""

import sys
import json
import time
from datetime import datetime
sys.path.insert(0, '.')

# Import all system components
from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor, ProcessingContext
from processing.hybrid_spacy_st_processor import HybridSpacySTProcessor
from mcp.mcp_hybrid_enhancements import enhance_search_with_hybrid_filtering

def full_system_validation():
    """Run comprehensive system validation"""
    
    print("🔬 Comprehensive System Validation")
    print("=" * 60)
    
    validation_results = {
        "validation_timestamp": datetime.now().isoformat(),
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "test_results": []
    }
    
    # Test 1: Database Integration
    test_name = "Database Integration"
    validation_results["tests_run"] += 1
    print(f"\n🧪 {test_name}")
    
    try:
        db = ClaudeVectorDatabase()
        entry_count = db.collection.count()
        
        # Test search functionality
        search_results = db.search_conversations("test query", n_results=3)
        
        result = {
            "test": test_name,
            "passed": entry_count > 40000 and len(search_results) > 0,
            "details": {
                "database_entries": entry_count,
                "search_results_returned": len(search_results),
                "database_healthy": entry_count > 40000
            }
        }
        
        if result["passed"]:
            print(f"   ✅ Database healthy: {entry_count} entries, search working")
            validation_results["tests_passed"] += 1
        else:
            print(f"   ❌ Database issues detected")
            validation_results["tests_failed"] += 1
            
        validation_results["test_results"].append(result)
        
    except Exception as e:
        print(f"   ❌ Database integration error: {e}")
        validation_results["tests_failed"] += 1
        validation_results["test_results"].append({
            "test": test_name,
            "passed": False,
            "error": str(e)
        })
    
    # Test 2: Hybrid Processing
    test_name = "Hybrid Processing"
    validation_results["tests_run"] += 1
    print(f"\n🧪 {test_name}")
    
    try:
        processor = HybridSpacySTProcessor()
        test_content = "I used the Edit tool to fix React TypeScript errors and now everything works perfectly"
        
        intelligence_results = processor.extract_intelligence(test_content)
        
        result = {
            "test": test_name,
            "passed": intelligence_results['hybrid_confidence'] > 0.3,
            "details": {
                "confidence": intelligence_results['hybrid_confidence'],
                "tools_detected": intelligence_results.get('technical_tools', '[]'),
                "frameworks_detected": intelligence_results.get('framework_mentions', '[]'),
                "extraction_successful": intelligence_results['hybrid_confidence'] > 0
            }
        }
        
        if result["passed"]:
            print(f"   ✅ Hybrid processing working: {intelligence_results['hybrid_confidence']:.3f} confidence")
            validation_results["tests_passed"] += 1
        else:
            print(f"   ⚠️ Low hybrid processing confidence: {intelligence_results['hybrid_confidence']:.3f}")
            validation_results["tests_failed"] += 1
            
        validation_results["test_results"].append(result)
        
    except Exception as e:
        print(f"   ❌ Hybrid processing error: {e}")
        validation_results["tests_failed"] += 1
        validation_results["test_results"].append({
            "test": test_name,
            "passed": False,
            "error": str(e)
        })
    
    # Test 3: Performance Validation
    test_name = "Performance Validation"
    validation_results["tests_run"] += 1
    print(f"\n🧪 {test_name}")
    
    try:
        processor = UnifiedEnhancementProcessor(enable_hybrid=True, suppress_init_logging=True)
        
        # Test processing performance
        start_time = time.time()
        test_entry = {
            'id': f'validation_test_{int(time.time())}',
            'content': 'Performance validation test for hybrid processing system',
            'type': 'assistant',
            'project_path': '/validation',
            'project_name': 'validation',
            'timestamp': datetime.now().isoformat()
        }
        
        enhanced_entry = processor.process_conversation_entry(
            test_entry,
            ProcessingContext(source="validation")
        )
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        result = {
            "test": test_name,
            "passed": processing_time < 250,  # 250ms tolerance
            "details": {
                "processing_time_ms": processing_time,
                "target_ms": 200,
                "within_tolerance": processing_time < 250,
                "hybrid_data_present": hasattr(enhanced_entry, 'hybrid_data')
            }
        }
        
        if result["passed"]:
            print(f"   ✅ Performance acceptable: {processing_time:.1f}ms")
            validation_results["tests_passed"] += 1
        else:
            print(f"   ⚠️ Performance slow: {processing_time:.1f}ms")
            validation_results["tests_failed"] += 1
            
        validation_results["test_results"].append(result)
        
    except Exception as e:
        print(f"   ❌ Performance validation error: {e}")
        validation_results["tests_failed"] += 1
        validation_results["test_results"].append({
            "test": test_name,
            "passed": False,
            "error": str(e)
        })
    
    # Test 4: Component Integration
    test_name = "Component Integration"
    validation_results["tests_run"] += 1
    print(f"\n🧪 {test_name}")
    
    try:
        processor = UnifiedEnhancementProcessor(enable_hybrid=True, suppress_init_logging=True)
        stats = processor.get_processor_stats()
        
        expected_components = 8  # Including hybrid
        actual_components = stats.get('components_available', 0)
        
        result = {
            "test": test_name,
            "passed": actual_components >= expected_components,
            "details": {
                "expected_components": expected_components,
                "actual_components": actual_components,
                "all_components_active": actual_components >= expected_components
            }
        }
        
        if result["passed"]:
            print(f"   ✅ All components active: {actual_components}/{expected_components}")
            validation_results["tests_passed"] += 1
        else:
            print(f"   ❌ Missing components: {actual_components}/{expected_components}")
            validation_results["tests_failed"] += 1
            
        validation_results["test_results"].append(result)
        
    except Exception as e:
        print(f"   ❌ Component integration error: {e}")
        validation_results["tests_failed"] += 1
        validation_results["test_results"].append({
            "test": test_name,
            "passed": False,
            "error": str(e)
        })
    
    # Final Assessment
    print("\n" + "=" * 60)
    total_tests = validation_results["tests_run"]
    passed_tests = validation_results["tests_passed"]
    failed_tests = validation_results["tests_failed"]
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Validation Summary:")
    print(f"   Tests Run: {total_tests}")
    print(f"   Tests Passed: {passed_tests}")
    print(f"   Tests Failed: {failed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 100:
        print("\n🎉 Perfect validation - System fully operational!")
        status = "excellent"
    elif success_rate >= 90:
        print("\n✅ Excellent validation - System ready for production!")
        status = "excellent"
    elif success_rate >= 75:
        print("\n⚠️ Good validation - Minor issues detected")
        status = "good"
    else:
        print("\n❌ Poor validation - Significant issues detected")
        status = "poor"
    
    validation_results["overall_status"] = status
    validation_results["success_rate"] = success_rate
    
    # Save validation results
    filename = f"system_validation_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📋 Detailed results saved to {filename}")
    
    return status == "excellent" or status == "good"

if __name__ == "__main__":
    success = full_system_validation()
    if not success:
        sys.exit(1)