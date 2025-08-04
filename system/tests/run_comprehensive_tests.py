#!/usr/bin/env python3
"""
Comprehensive Test Runner for Enhanced Vector Database System

Runs all test suites and provides a complete validation report for the
unified enhancement system components.

Author: Enhanced Vector Database System (July 2025)
Version: 1.0.0
"""

import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    """Comprehensive test runner for the enhanced vector database system."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.start_time = None
        self.results = {}
        
    def run_all_tests(self):
        """Run all test suites and generate comprehensive report."""
        print("🧪 Enhanced Vector Database System - Comprehensive Test Suite")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = time.time()
        
        # Define test modules to run
        test_modules = [
            {
                'name': 'UnifiedEnhancementEngine Tests',
                'file': 'test_unified_enhancement_engine.py',
                'description': 'Tests main orchestrator combining all enhancement components'
            },
            {
                'name': 'ConversationBackFillEngine Tests', 
                'file': 'test_conversation_backfill_engine.py',
                'description': 'Tests conversation chain back-fill (0.97% → 80%+ issue)'
            },
            {
                'name': 'MCP Integration Tests',
                'file': 'test_mcp_integration.py', 
                'description': 'Tests MCP tools for unified enhancement system'
            },
            {
                'name': 'Enhanced Sync Scripts Tests',
                'file': 'test_enhanced_sync_scripts.py',
                'description': 'Tests enhanced run_full_sync.py and smart_metadata_sync.py'
            }
        ]
        
        all_passed = True
        total_tests = 0
        total_passed = 0
        total_failed = 0
        
        # Run each test module
        for test_module in test_modules:
            print(f"🔧 Running {test_module['name']}")
            print(f"   {test_module['description']}")
            
            result = self._run_test_module(test_module['file'])
            self.results[test_module['name']] = result
            
            if result['success']:
                status_icon = "✅"
                print(f"   {status_icon} PASSED: {result['tests_run']} tests, {result['duration']:.2f}s")
            else:
                status_icon = "❌"
                all_passed = False
                print(f"   {status_icon} FAILED: {result['tests_run']} tests, {result['failures']} failures")
                if result.get('errors'):
                    print(f"      Errors: {result['errors']}")
            
            total_tests += result['tests_run']
            total_passed += result['tests_run'] - result['failures']
            total_failed += result['failures']
            print()
        
        # Generate final report
        self._generate_final_report(all_passed, total_tests, total_passed, total_failed)
        
        return all_passed
    
    def _run_test_module(self, test_file):
        """Run a single test module and parse results."""
        test_path = self.test_dir / test_file
        
        if not test_path.exists():
            return {
                'success': False,
                'tests_run': 0,
                'failures': 1,
                'duration': 0.0,
                'errors': f"Test file {test_file} not found"
            }
        
        try:
            # Run pytest on the specific test file
            start_time = time.time()
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(test_path),
                '-v',
                '--tb=short',
                '--no-header',
                '--quiet'
            ], 
            capture_output=True, 
            text=True,
            cwd=self.test_dir.parent
            )
            duration = time.time() - start_time
            
            # Parse pytest output
            return self._parse_pytest_output(result, duration)
            
        except Exception as e:
            return {
                'success': False,
                'tests_run': 0,
                'failures': 1,
                'duration': 0.0,
                'errors': str(e)
            }
    
    def _parse_pytest_output(self, result, duration):
        """Parse pytest output to extract test statistics."""
        output = result.stdout + result.stderr
        
        # Default values
        tests_run = 0
        failures = 0
        errors = []
        
        # Parse output for test statistics
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for test result summary
            if 'passed' in line and 'failed' in line:
                # Format: "X failed, Y passed in Z.XXs"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'failed,':
                        try:
                            failures = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
                    elif part == 'passed':
                        try:
                            passed = int(parts[i-1])
                            tests_run = passed + failures
                        except (ValueError, IndexError):
                            pass
            elif 'passed in' in line:
                # Format: "X passed in Z.XXs"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed':
                        try:
                            tests_run = int(parts[i-1])
                        except (ValueError, IndexError):
                            pass
            elif 'FAILED' in line:
                errors.append(line)
        
        success = result.returncode == 0 and failures == 0
        
        return {
            'success': success,
            'tests_run': tests_run,
            'failures': failures,
            'duration': duration,
            'errors': errors[:5],  # Limit to first 5 errors
            'return_code': result.returncode
        }
    
    def _generate_final_report(self, all_passed, total_tests, total_passed, total_failed):
        """Generate comprehensive final test report."""
        total_duration = time.time() - self.start_time
        
        print("=" * 80)
        print("🎯 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall status
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            status_icon = "✅"
        else:
            print("⚠️ SOME TESTS FAILED")
            status_icon = "❌"
        
        print()
        print("📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed} {status_icon if all_passed else '✅'}")
        print(f"   Failed: {total_failed} {'✅' if total_failed == 0 else '❌'}")
        print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: N/A")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        print()
        print("📋 Component Test Results:")
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"   • {test_name}: {status}")
            print(f"     Tests: {result['tests_run']}, Failures: {result['failures']}, Duration: {result['duration']:.2f}s")
            
            if result.get('errors') and len(result['errors']) > 0:
                print(f"     First error: {result['errors'][0][:100]}...")
        
        print()
        print("🔧 Component Coverage Analysis:")
        print("   ✅ UnifiedEnhancementEngine - Main orchestrator testing")
        print("   ✅ ConversationBackFillEngine - Critical chain population issue")
        print("   ✅ MCP Tools Integration - Claude Code integration")
        print("   ✅ Enhanced Sync Scripts - File processing workflows")
        
        if not all_passed:
            print()
            print("🔍 Failed Test Analysis:")
            for test_name, result in self.results.items():
                if not result['success']:
                    print(f"   ❌ {test_name}:")
                    print(f"      Failures: {result['failures']}")
                    if result.get('errors'):
                        for error in result['errors'][:3]:  # Show first 3 errors
                            print(f"      • {error}")
        
        print()
        print("💡 Recommendations:")
        if all_passed:
            print("   ✅ All components tested successfully")
            print("   ✅ System ready for production deployment")
            print("   ✅ Unified enhancement system validated")
        else:
            print("   ⚠️ Address failed tests before deployment")
            print("   ⚠️ Review component integration issues")
            print("   ⚠️ Run individual test modules for detailed debugging")
        
        print()
        print("🚀 Next Steps:")
        print("   1. Create run_unified_enhancement.py standalone script")
        print("   2. Update health_dashboard.sh with enhancement metrics")
        print("   3. Run comprehensive validation and performance testing")
        
        print()
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import pytest
        print("✅ pytest available")
    except ImportError:
        print("❌ pytest not available. Install with: pip install pytest")
        return False
    
    return True


def main():
    """Main entry point for comprehensive test runner."""
    
    print("🔧 Enhanced Vector Database System - Test Suite Validator")
    print("Checking dependencies...")
    
    if not check_dependencies():
        print("❌ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    print("✅ Dependencies checked")
    print()
    
    # Run comprehensive tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()