#!/usr/bin/env python3
"""
Outcome Certainty Range Fix

Specific incremental update to fix outcome_certainty values that exceed 1.0.
This addresses the validation error in EnhancedConversationEntry where outcome_certainty 
should be in range [0.0, 1.0] but some entries have values > 1.0.

Usage:
    # Scan for outcome_certainty issues
    python update_outcome_certainty_fix.py --scan
    
    # Apply fix (dry run first)
    python update_outcome_certainty_fix.py --fix --dry-run
    
    # Apply fix for real
    python update_outcome_certainty_fix.py --fix --apply
    
    # Full workflow with validation
    python update_outcome_certainty_fix.py --scan --fix --apply --validate
"""

import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import argparse

from incremental_database_updater import IncrementalDatabaseUpdater, ValidationIssue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OutcomeCertaintyFixer:
    """Specialized fixer for outcome_certainty range issues"""
    
    def __init__(self):
        self.updater = IncrementalDatabaseUpdater()
        self.issue_type = "outcome_certainty_range"
        self.fix_name = "outcome_certainty_range_fix"
    
    def scan_for_issues(self) -> List[ValidationIssue]:
        """Scan database for outcome_certainty range issues"""
        logger.info("🔍 Scanning for outcome_certainty values > 1.0...")
        
        return self.updater.scan_for_issues(
            issue_type=self.issue_type,
            batch_size=1000
        )
    
    def apply_fix(self, issues: List[ValidationIssue], dry_run: bool = True):
        """Apply the outcome_certainty range fix"""
        if not issues:
            logger.info("✅ No outcome_certainty issues found to fix")
            return None
        
        logger.info(f"🔧 Applying outcome_certainty fix to {len(issues)} issues...")
        
        # Create rollback snapshot before applying fix
        entry_ids = [issue.entry_id for issue in issues]
        snapshot_path = None
        
        if not dry_run:
            snapshot_path = self.updater.create_rollback_snapshot(entry_ids)
            logger.info(f"📸 Rollback snapshot created: {snapshot_path}")
        
        # Apply the fix
        result = self.updater.apply_targeted_fix(
            fix_name=self.fix_name,
            issues=issues,
            dry_run=dry_run,
            batch_size=100
        )
        
        # Add snapshot info to result
        if snapshot_path:
            result.details["rollback_snapshot"] = snapshot_path
        
        return result
    
    def validate_fix(self, apply_result):
        """Validate that the fix was applied successfully"""
        if not apply_result:
            return None
        
        logger.info("🔍 Validating outcome_certainty fix...")
        
        validation_report = self.updater.validate_fix(
            fix_result=apply_result,
            re_scan_issues=True
        )
        
        return validation_report
    
    def custom_outcome_certainty_validator(self, entry_id: str, metadata: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Custom validator specifically for outcome_certainty issues.
        
        More comprehensive than the built-in validator - checks for:
        - Values > 1.0 (should be clamped to 1.0)
        - Negative values (should be clamped to 0.0)  
        - Non-numeric values (should be set to 0.0)
        """
        issues = []
        
        outcome_certainty = metadata.get('outcome_certainty')
        
        # Check if field exists
        if outcome_certainty is None:
            issues.append(ValidationIssue(
                entry_id=entry_id,
                issue_type="outcome_certainty_missing",
                field_name="outcome_certainty",
                current_value=None,
                expected_value=0.0,
                severity="info",
                description="outcome_certainty field is missing"
            ))
            return issues
        
        # Check if it's numeric
        if not isinstance(outcome_certainty, (int, float)):
            issues.append(ValidationIssue(
                entry_id=entry_id,
                issue_type="outcome_certainty_non_numeric",
                field_name="outcome_certainty",
                current_value=outcome_certainty,
                expected_value=0.0,
                severity="critical",
                description=f"outcome_certainty is non-numeric: {type(outcome_certainty).__name__}"
            ))
            return issues
        
        # Check range violations
        if outcome_certainty < 0.0:
            issues.append(ValidationIssue(
                entry_id=entry_id,
                issue_type="outcome_certainty_negative",
                field_name="outcome_certainty",
                current_value=outcome_certainty,
                expected_value=0.0,
                severity="critical",
                description=f"outcome_certainty {outcome_certainty} is negative"
            ))
        
        elif outcome_certainty > 1.0:
            issues.append(ValidationIssue(
                entry_id=entry_id,
                issue_type="outcome_certainty_too_high",
                field_name="outcome_certainty",
                current_value=outcome_certainty,
                expected_value=1.0,
                severity="critical",
                description=f"outcome_certainty {outcome_certainty} exceeds maximum of 1.0"
            ))
        
        return issues
    
    def comprehensive_scan(self) -> Dict[str, List[ValidationIssue]]:
        """Perform comprehensive scan for all outcome_certainty issues"""
        logger.info("🔍 Performing comprehensive outcome_certainty scan...")
        
        all_issues = self.updater.scan_for_issues(
            issue_type="custom_outcome_certainty",
            batch_size=1000,
            custom_validator=self.custom_outcome_certainty_validator
        )
        
        # Group issues by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue.issue_type
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Print summary
        logger.info("📊 Comprehensive scan results:")
        for issue_type, issues in issues_by_type.items():
            logger.info(f"  - {issue_type}: {len(issues)} issues")
        
        return issues_by_type
    
    def custom_fix_function(self, entry_id: str, metadata: Dict[str, Any], issues: List[ValidationIssue]) -> Dict[str, Any]:
        """
        Custom fix function for outcome_certainty issues.
        
        Handles:
        - Clamping values to [0.0, 1.0] range
        - Converting non-numeric values to 0.0
        - Adding missing fields with default value 0.0
        """
        updated_metadata = metadata.copy()
        
        for issue in issues:
            if issue.field_name == "outcome_certainty":
                if issue.issue_type == "outcome_certainty_missing":
                    updated_metadata["outcome_certainty"] = 0.0
                
                elif issue.issue_type == "outcome_certainty_non_numeric":
                    updated_metadata["outcome_certainty"] = 0.0
                
                elif issue.issue_type == "outcome_certainty_negative":
                    updated_metadata["outcome_certainty"] = 0.0
                
                elif issue.issue_type == "outcome_certainty_too_high":
                    updated_metadata["outcome_certainty"] = 1.0
                
                else:
                    # Generic clamping for any other outcome_certainty issues
                    current_value = issue.current_value
                    if isinstance(current_value, (int, float)):
                        updated_metadata["outcome_certainty"] = max(0.0, min(1.0, current_value))
                    else:
                        updated_metadata["outcome_certainty"] = 0.0
        
        return updated_metadata
    
    def run_full_workflow(self, dry_run: bool = True, validate: bool = True) -> Dict[str, Any]:
        """
        Run the complete outcome_certainty fix workflow.
        
        Steps:
        1. Scan for issues
        2. Apply fixes (with rollback snapshot)
        3. Validate fixes worked
        4. Generate summary report
        """
        workflow_start = time.time()
        logger.info("🚀 Starting complete outcome_certainty fix workflow...")
        
        workflow_results = {
            "workflow_start": datetime.now().isoformat(),
            "dry_run": dry_run,
            "validate": validate,
            "steps": {}
        }
        
        try:
            # Step 1: Comprehensive scan
            logger.info("📋 Step 1: Comprehensive scan for outcome_certainty issues...")
            issues_by_type = self.comprehensive_scan()
            
            all_issues = []
            for issues_list in issues_by_type.values():
                all_issues.extend(issues_list)
            
            workflow_results["steps"]["scan"] = {
                "total_issues": len(all_issues),
                "issues_by_type": {k: len(v) for k, v in issues_by_type.items()},
                "success": True
            }
            
            if not all_issues:
                logger.info("✅ No outcome_certainty issues found!")
                workflow_results["overall_success"] = True
                workflow_results["workflow_time"] = time.time() - workflow_start
                return workflow_results
            
            # Step 2: Apply fixes
            logger.info(f"📋 Step 2: Applying fixes to {len(all_issues)} issues...")
            
            fix_result = self.updater.apply_targeted_fix(
                fix_name="comprehensive_outcome_certainty_fix",
                issues=all_issues,
                fix_function=self.custom_fix_function,
                dry_run=dry_run,
                batch_size=100
            )
            
            workflow_results["steps"]["fix"] = {
                "fixes_applied": fix_result.fixes_applied,
                "errors": fix_result.errors_encountered,
                "execution_time": fix_result.execution_time_seconds,
                "rollback_snapshot": fix_result.details.get("rollback_snapshot"),
                "success": fix_result.errors_encountered == 0
            }
            
            # Step 3: Validation (if requested and not dry run)
            if validate and not dry_run:
                logger.info("📋 Step 3: Validating fixes...")
                
                validation_report = self.validate_fix(fix_result)
                workflow_results["steps"]["validation"] = {
                    "validation_successful": validation_report["validation_successful"],
                    "issues_remaining": validation_report["issues_remaining"],
                    "success": validation_report["validation_successful"]
                }
            elif validate and dry_run:
                logger.info("📋 Step 3: Skipping validation (dry run mode)")  
                workflow_results["steps"]["validation"] = {
                    "skipped": "dry_run_mode",
                    "success": True
                }
            
            # Overall success
            all_steps_successful = all(
                step_result.get("success", False) 
                for step_result in workflow_results["steps"].values()
            )
            
            workflow_results["overall_success"] = all_steps_successful
            workflow_results["workflow_time"] = time.time() - workflow_start
            
            logger.info(f"🎯 Workflow complete: {'SUCCESS' if all_steps_successful else 'PARTIAL'} ({workflow_results['workflow_time']:.2f}s)")
            
            return workflow_results
        
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            workflow_results["error"] = str(e)
            workflow_results["overall_success"] = False
            workflow_results["workflow_time"] = time.time() - workflow_start
            return workflow_results
    
    def generate_fix_report(self, workflow_results: Dict[str, Any]) -> str:
        """Generate a human-readable fix report"""
        
        report_lines = [
            "=" * 60,
            "OUTCOME CERTAINTY FIX REPORT",
            "=" * 60,
            f"Timestamp: {workflow_results.get('workflow_start', 'Unknown')}",
            f"Mode: {'DRY RUN' if workflow_results.get('dry_run') else 'LIVE UPDATE'}",
            f"Overall Success: {'✅ YES' if workflow_results.get('overall_success') else '❌ NO'}",
            f"Total Time: {workflow_results.get('workflow_time', 0):.2f} seconds",
            "",
            "STEP RESULTS:",
        ]
        
        steps = workflow_results.get("steps", {})
        
        # Scan results
        if "scan" in steps:
            scan = steps["scan"]
            report_lines.extend([
                f"  📊 SCAN: {'✅' if scan.get('success') else '❌'}",
                f"     Total Issues Found: {scan.get('total_issues', 0)}",
            ])
            
            for issue_type, count in scan.get("issues_by_type", {}).items():
                report_lines.append(f"     - {issue_type}: {count}")
            
            report_lines.append("")
        
        # Fix results
        if "fix" in steps:
            fix = steps["fix"]
            report_lines.extend([
                f"  🔧 FIX: {'✅' if fix.get('success') else '❌'}",
                f"     Fixes Applied: {fix.get('fixes_applied', 0)}",
                f"     Errors: {fix.get('errors', 0)}",
                f"     Execution Time: {fix.get('execution_time', 0):.2f}s",
            ])
            
            if fix.get("rollback_snapshot"):
                report_lines.append(f"     Rollback Snapshot: {fix['rollback_snapshot']}")
            
            report_lines.append("")
        
        # Validation results
        if "validation" in steps:
            validation = steps["validation"]
            if validation.get("skipped"):
                report_lines.extend([
                    f"  🔍 VALIDATION: ⏭️ SKIPPED ({validation['skipped']})",
                    ""
                ])
            else:
                report_lines.extend([
                    f"  🔍 VALIDATION: {'✅' if validation.get('success') else '❌'}",
                    f"     Validation Successful: {'Yes' if validation.get('validation_successful') else 'No'}",
                    f"     Issues Remaining: {validation.get('issues_remaining', 'Unknown')}",
                    ""
                ])
        
        # Summary and recommendations
        report_lines.extend([
            "SUMMARY:",
        ])
        
        if workflow_results.get("overall_success"):
            report_lines.append("  ✅ All outcome_certainty issues have been resolved successfully!")
        else:
            report_lines.append("  ⚠️  Some issues encountered during the fix process.")
        
        if workflow_results.get("dry_run"):
            report_lines.extend([
                "",
                "NEXT STEPS:",
                "  This was a dry run. To apply the fixes:",
                "  python update_outcome_certainty_fix.py --fix --apply"
            ])
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)


def main():
    """Command-line interface for outcome_certainty fix"""
    parser = argparse.ArgumentParser(description="Fix outcome_certainty range issues")
    parser.add_argument("--scan", action="store_true", help="Scan for outcome_certainty issues")
    parser.add_argument("--fix", action="store_true", help="Apply fixes")
    parser.add_argument("--dry-run", action="store_true", help="Simulate fixes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply fixes for real (overrides dry-run)")
    parser.add_argument("--validate", action="store_true", help="Validate fixes after applying")
    parser.add_argument("--comprehensive", action="store_true", help="Use comprehensive scan")
    parser.add_argument("--workflow", action="store_true", help="Run complete workflow")
    
    args = parser.parse_args()
    
    fixer = OutcomeCertaintyFixer()
    
    if args.workflow:
        # Run complete workflow
        dry_run = not args.apply
        workflow_results = fixer.run_full_workflow(dry_run=dry_run, validate=args.validate)
        
        # Generate and display report
        report = fixer.generate_fix_report(workflow_results)
        print(report)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/home/user/.claude-vector-db-enhanced/update_results/outcome_certainty_workflow_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(workflow_results, f, indent=2)
        print(f"\n📁 Detailed results saved: {results_file}")
    
    elif args.scan:
        if args.comprehensive:
            issues_by_type = fixer.comprehensive_scan()
            total_issues = sum(len(issues) for issues in issues_by_type.values())
            print(f"\n📊 Comprehensive scan found {total_issues} issues:")
            for issue_type, issues in issues_by_type.items():
                print(f"  - {issue_type}: {len(issues)}")
                if issues:
                    print(f"    Sample: {issues[0].description}")
        else:
            issues = fixer.scan_for_issues()
            print(f"\n📊 Found {len(issues)} outcome_certainty > 1.0 issues")
            if issues:
                print("Sample issues:")
                for issue in issues[:5]:
                    print(f"  - {issue.entry_id}: {issue.description}")
    
    elif args.fix:
        # Scan first
        issues = fixer.scan_for_issues()
        
        if not issues:
            print("✅ No outcome_certainty issues found to fix")
            return
        
        # Apply fix
        dry_run = not args.apply
        result = fixer.apply_fix(issues, dry_run=dry_run)
        
        print(f"\n🔧 Fix {'simulated' if dry_run else 'applied'}:")
        print(f"  - Issues found: {result.issues_found}")
        print(f"  - Fixes applied: {result.fixes_applied}")
        print(f"  - Errors: {result.errors_encountered}")
        print(f"  - Time: {result.execution_time_seconds:.2f}s")
        
        if result.details.get("rollback_snapshot"):
            print(f"  - Rollback snapshot: {result.details['rollback_snapshot']}")
        
        # Validate if requested
        if args.validate and not dry_run:
            validation = fixer.validate_fix(result)
            print(f"\n🔍 Validation: {'✅ PASSED' if validation['validation_successful'] else '❌ FAILED'}")
            print(f"  - Issues remaining: {validation['issues_remaining']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()