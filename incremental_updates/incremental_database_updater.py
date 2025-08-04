#!/usr/bin/env python3
"""
Incremental Database Updater for Claude Vector Database

This system provides efficient incremental updates for the enhanced conversation database:
- Schema updates for fixing metadata fields
- Selective re-processing of entries that need fixes
- Field-specific updates without full re-processing
- Validation and rollback capabilities
- Progress tracking and performance monitoring

Usage Examples:
    # Fix outcome_certainty range issue
    python incremental_database_updater.py --scan-issue outcome_certainty_range
    python incremental_database_updater.py --fix outcome_certainty_range --dry-run
    python incremental_database_updater.py --fix outcome_certainty_range --apply

    # Fix missing realtime_learning_boost fields (new Real-time Learning component)
    python incremental_database_updater.py --scan-issue missing_enhancement_fields
    python incremental_database_updater.py --fix missing_enhancement_fields --apply

    # Update specific field across all entries
    python incremental_database_updater.py --update-field validation_strength --value-transform "max(-1.0, min(1.0, x))"
    
    # Custom validation and fix
    updater = IncrementalDatabaseUpdater()
    issues = updater.scan_for_issues("custom_validation", custom_validator=my_validator)
    updater.apply_targeted_fix("custom_fix", issues, fix_function=my_fix_function)
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import traceback

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vector_database import ClaudeVectorDatabase

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class UpdateResult:
    """Result of an incremental update operation"""
    update_type: str
    total_scanned: int
    issues_found: int
    fixes_applied: int
    errors_encountered: int
    execution_time_seconds: float
    dry_run: bool
    timestamp: str
    details: Dict[str, Any]


@dataclass 
class ValidationIssue:
    """Represents a validation issue found in the database"""
    entry_id: str
    issue_type: str
    field_name: str
    current_value: Any
    expected_value: Any
    severity: str  # "critical", "warning", "info"
    description: str


class IncrementalDatabaseUpdater:
    """
    Incremental update system for the enhanced conversation database.
    
    Provides efficient targeted updates without requiring full database rebuilds.
    """
    
    def __init__(self, db_path: str = "/home/user/.claude-vector-db-enhanced/chroma_db"):
        """Initialize the updater with database connection"""
        self.db = ClaudeVectorDatabase(db_path=db_path)
        self.results_dir = Path("/home/user/.claude-vector-db-enhanced/update_results")
        self.results_dir.mkdir(exist_ok=True)
        
        logger.info(f"🔧 Initialized incremental updater for database: {db_path}")
        logger.info(f"📊 Database has {self.db.collection.count()} entries")
    
    def scan_for_issues(self, 
                       issue_type: str, 
                       batch_size: int = 1000,
                       custom_validator: Optional[Callable] = None) -> List[ValidationIssue]:
        """
        Scan database for specific types of issues.
        
        Args:
            issue_type: Type of issue to scan for (e.g., "outcome_certainty_range")
            batch_size: Size of batches to process for memory efficiency
            custom_validator: Optional custom validation function
            
        Returns:
            List of ValidationIssue objects found
        """
        logger.info(f"🔍 Scanning database for '{issue_type}' issues...")
        start_time = time.time()
        
        issues = []
        total_scanned = 0
        
        # Get all entries in batches
        try:
            offset = 0
            while True:
                # Fetch batch of entries with metadata
                batch_data = self.db.collection.get(
                    limit=batch_size,
                    offset=offset,
                    include=["metadatas", "documents"]
                )
                
                if not batch_data['ids']:
                    break
                
                # Process this batch
                batch_issues = self._validate_batch(
                    batch_data, 
                    issue_type, 
                    custom_validator
                )
                issues.extend(batch_issues)
                
                total_scanned += len(batch_data['ids'])
                offset += batch_size
                
                logger.info(f"📊 Scanned {total_scanned} entries, found {len(issues)} issues so far...")
        
        except Exception as e:
            logger.error(f"Error during scan: {e}")
            logger.error(traceback.format_exc())
            raise
        
        scan_time = time.time() - start_time
        logger.info(f"✅ Scan complete: {len(issues)} issues found in {total_scanned} entries ({scan_time:.2f}s)")
        
        # Save scan results
        self._save_scan_results(issue_type, issues, total_scanned, scan_time)
        
        return issues
    
    def _validate_batch(self, 
                       batch_data: Dict[str, List], 
                       issue_type: str,
                       custom_validator: Optional[Callable] = None) -> List[ValidationIssue]:
        """Validate a batch of entries for specific issues"""
        issues = []
        
        for i, entry_id in enumerate(batch_data['ids']):
            try:
                metadata = batch_data['metadatas'][i]
                
                if custom_validator:
                    # Use custom validator
                    batch_issues = custom_validator(entry_id, metadata)
                    if batch_issues:
                        issues.extend(batch_issues)
                else:
                    # Use built-in validators
                    batch_issues = self._apply_builtin_validator(entry_id, metadata, issue_type)
                    issues.extend(batch_issues)
                    
            except Exception as e:
                logger.warning(f"Error validating entry {entry_id}: {e}")
                continue
        
        return issues
    
    def _apply_builtin_validator(self, 
                               entry_id: str, 
                               metadata: Dict[str, Any], 
                               issue_type: str) -> List[ValidationIssue]:
        """Apply built-in validation rules"""
        issues = []
        
        if issue_type == "outcome_certainty_range":
            # Check if outcome_certainty is > 1.0 (should be 0.0-1.0)
            outcome_certainty = metadata.get('outcome_certainty', 0.0)
            if isinstance(outcome_certainty, (int, float)) and outcome_certainty > 1.0:
                issues.append(ValidationIssue(
                    entry_id=entry_id,
                    issue_type="outcome_certainty_range",
                    field_name="outcome_certainty",
                    current_value=outcome_certainty,
                    expected_value=min(1.0, outcome_certainty),
                    severity="critical",
                    description=f"outcome_certainty {outcome_certainty} exceeds maximum of 1.0"
                ))
        
        elif issue_type == "validation_strength_range":
            # Check if validation_strength is outside [-1.0, 1.0]
            validation_strength = metadata.get('validation_strength', 0.0)
            if isinstance(validation_strength, (int, float)) and abs(validation_strength) > 1.0:
                clamped_value = max(-1.0, min(1.0, validation_strength))
                issues.append(ValidationIssue(
                    entry_id=entry_id,
                    issue_type="validation_strength_range",
                    field_name="validation_strength",
                    current_value=validation_strength,
                    expected_value=clamped_value,
                    severity="critical", 
                    description=f"validation_strength {validation_strength} outside range [-1.0, 1.0]"
                ))
        
        elif issue_type == "topic_confidence_range":
            # Check if topic_confidence is outside [0.0, 2.0]
            topic_confidence = metadata.get('topic_confidence', 0.0)
            if isinstance(topic_confidence, (int, float)) and (topic_confidence < 0.0 or topic_confidence > 2.0):
                clamped_value = max(0.0, min(2.0, topic_confidence))
                issues.append(ValidationIssue(
                    entry_id=entry_id,
                    issue_type="topic_confidence_range",
                    field_name="topic_confidence",
                    current_value=topic_confidence,
                    expected_value=clamped_value,
                    severity="warning",
                    description=f"topic_confidence {topic_confidence} outside range [0.0, 2.0]"
                ))
        
        elif issue_type == "solution_quality_range":
            # Check if solution_quality_score is outside [0.1, 3.0]
            solution_quality = metadata.get('solution_quality_score', 1.0)
            if isinstance(solution_quality, (int, float)) and (solution_quality < 0.1 or solution_quality > 3.0):
                clamped_value = max(0.1, min(3.0, solution_quality))
                issues.append(ValidationIssue(
                    entry_id=entry_id,
                    issue_type="solution_quality_range",
                    field_name="solution_quality_score",
                    current_value=solution_quality,
                    expected_value=clamped_value,
                    severity="warning",
                    description=f"solution_quality_score {solution_quality} outside range [0.1, 3.0]"
                ))
        
        elif issue_type == "realtime_learning_boost_range":
            # Check if realtime_learning_boost is outside [0.1, 3.0]
            realtime_boost = metadata.get('realtime_learning_boost', 1.0)
            if isinstance(realtime_boost, (int, float)) and (realtime_boost < 0.1 or realtime_boost > 3.0):
                clamped_value = max(0.1, min(3.0, realtime_boost))
                issues.append(ValidationIssue(
                    entry_id=entry_id,
                    issue_type="realtime_learning_boost_range",
                    field_name="realtime_learning_boost",
                    current_value=realtime_boost,
                    expected_value=clamped_value,
                    severity="warning",
                    description=f"realtime_learning_boost {realtime_boost} outside range [0.1, 3.0]"
                ))
        
        elif issue_type == "missing_enhancement_fields":
            # Check for entries missing key enhancement fields
            required_fields = [
                'detected_topics', 'primary_topic', 'topic_confidence',
                'solution_quality_score', 'validation_strength', 'outcome_certainty',
                'realtime_learning_boost'  # New real-time learning field
            ]
            
            for field in required_fields:
                if field not in metadata:
                    issues.append(ValidationIssue(
                        entry_id=entry_id,
                        issue_type="missing_enhancement_fields",
                        field_name=field,
                        current_value=None,
                        expected_value="<default_value>",
                        severity="info",
                        description=f"Missing enhancement field: {field}"
                    ))
        
        return issues
    
    def apply_targeted_fix(self, 
                          fix_name: str,
                          issues: List[ValidationIssue],
                          fix_function: Optional[Callable] = None,
                          dry_run: bool = True,
                          batch_size: int = 100) -> UpdateResult:
        """
        Apply targeted fixes to specific issues.
        
        Args:
            fix_name: Name of the fix being applied
            issues: List of issues to fix
            fix_function: Custom fix function (entry_id, metadata) -> updated_metadata
            dry_run: If True, only simulate the fix without applying
            batch_size: Size of batches for update operations
            
        Returns:
            UpdateResult with statistics and details
        """
        logger.info(f"🔧 Applying fix '{fix_name}' to {len(issues)} issues (dry_run={dry_run})")
        start_time = time.time()
        
        fixes_applied = 0
        errors_encountered = 0
        
        # Group issues by entry_id for batch processing
        issues_by_entry = {}
        for issue in issues:
            if issue.entry_id not in issues_by_entry:
                issues_by_entry[issue.entry_id] = []
            issues_by_entry[issue.entry_id].append(issue)
        
        # Process fixes in batches
        entry_ids = list(issues_by_entry.keys())
        
        for i in range(0, len(entry_ids), batch_size):
            batch_entry_ids = entry_ids[i:i + batch_size]
            
            try:
                # Get current data for this batch
                batch_data = self.db.collection.get(
                    ids=batch_entry_ids,
                    include=["metadatas", "documents"]
                )
                
                # Apply fixes to each entry in batch
                updated_metadatas = []
                updated_ids = []
                
                for j, entry_id in enumerate(batch_data['ids']):
                    try:
                        current_metadata = batch_data['metadatas'][j]
                        entry_issues = issues_by_entry[entry_id]
                        
                        # Apply fixes
                        if fix_function:
                            # Use custom fix function
                            updated_metadata = fix_function(entry_id, current_metadata, entry_issues)
                        else:
                            # Use built-in fix logic
                            updated_metadata = self._apply_builtin_fix(
                                current_metadata, entry_issues, fix_name
                            )
                        
                        if updated_metadata != current_metadata:
                            updated_metadatas.append(updated_metadata)
                            updated_ids.append(entry_id)
                            fixes_applied += 1
                    
                    except Exception as e:
                        logger.error(f"Error fixing entry {entry_id}: {e}")
                        errors_encountered += 1
                        continue
                
                # Apply batch update if not dry run
                if not dry_run and updated_metadatas:
                    self.db.collection.update(
                        ids=updated_ids,
                        metadatas=updated_metadatas
                    )
                    logger.info(f"✅ Updated batch {i//batch_size + 1}: {len(updated_metadatas)} entries")
                elif dry_run and updated_metadatas:
                    logger.info(f"🔍 [DRY RUN] Would update batch {i//batch_size + 1}: {len(updated_metadatas)} entries")
            
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                errors_encountered += batch_size
                continue
        
        execution_time = time.time() - start_time
        
        # Create result
        result = UpdateResult(
            update_type=fix_name,
            total_scanned=len(issues),
            issues_found=len(issues),
            fixes_applied=fixes_applied,
            errors_encountered=errors_encountered,
            execution_time_seconds=execution_time,
            dry_run=dry_run,
            timestamp=datetime.now().isoformat(),
            details={
                "batch_size": batch_size,
                "unique_entries_affected": len(issues_by_entry)
            }
        )
        
        logger.info(f"✅ Fix '{fix_name}' complete: {fixes_applied} applied, {errors_encountered} errors ({execution_time:.2f}s)")
        
        # Save result
        self._save_update_result(result)
        
        return result
    
    def _apply_builtin_fix(self, 
                          metadata: Dict[str, Any], 
                          issues: List[ValidationIssue],
                          fix_name: str) -> Dict[str, Any]:
        """Apply built-in fix logic for common issues"""
        updated_metadata = metadata.copy()
        
        for issue in issues:
            if issue.issue_type == "outcome_certainty_range":
                # Clamp outcome_certainty to [0.0, 1.0]
                updated_metadata['outcome_certainty'] = min(1.0, max(0.0, issue.current_value))
            
            elif issue.issue_type == "validation_strength_range":
                # Clamp validation_strength to [-1.0, 1.0]
                updated_metadata['validation_strength'] = max(-1.0, min(1.0, issue.current_value))
            
            elif issue.issue_type == "topic_confidence_range":
                # Clamp topic_confidence to [0.0, 2.0]
                updated_metadata['topic_confidence'] = max(0.0, min(2.0, issue.current_value))
            
            elif issue.issue_type == "solution_quality_range":
                # Clamp solution_quality_score to [0.1, 3.0]
                updated_metadata['solution_quality_score'] = max(0.1, min(3.0, issue.current_value))
            
            elif issue.issue_type == "realtime_learning_boost_range":
                # Clamp realtime_learning_boost to [0.1, 3.0]
                updated_metadata['realtime_learning_boost'] = max(0.1, min(3.0, issue.current_value))
            
            elif issue.issue_type == "missing_enhancement_fields":
                # Add missing fields with defaults
                field_defaults = {
                    'detected_topics': '{}',
                    'primary_topic': '',
                    'topic_confidence': 0.0,
                    'solution_quality_score': 1.0,
                    'validation_strength': 0.0,
                    'outcome_certainty': 0.0,
                    'has_success_markers': False,
                    'has_quality_indicators': False,
                    'previous_message_id': '',
                    'next_message_id': '',
                    'message_sequence_position': 0,
                    'user_feedback_sentiment': '',
                    'is_validated_solution': False,
                    'is_refuted_attempt': False,
                    'is_solution_attempt': False,
                    'is_feedback_to_solution': False,
                    'related_solution_id': '',
                    'feedback_message_id': '',
                    'solution_category': '',
                    # ✨ Real-time Feedback Loop Learning fields
                    'realtime_learning_boost': 1.0
                }
                
                if issue.field_name in field_defaults:
                    updated_metadata[issue.field_name] = field_defaults[issue.field_name]
        
        return updated_metadata
    
    def validate_fix(self, 
                    fix_result: UpdateResult,
                    re_scan_issues: bool = True) -> Dict[str, Any]:
        """
        Validate that a fix was applied correctly.
        
        Args:
            fix_result: Result of the fix operation to validate
            re_scan_issues: Whether to re-scan for the same issues
            
        Returns:
            Validation report with success/failure details
        """
        logger.info(f"🔍 Validating fix '{fix_result.update_type}'...")
        
        validation_report = {
            "fix_name": fix_result.update_type,
            "validation_timestamp": datetime.now().isoformat(),
            "fixes_applied": fix_result.fixes_applied,
            "validation_successful": False,
            "issues_remaining": 0,
            "details": {}
        }
        
        if re_scan_issues:
            # Re-scan for the same type of issues
            remaining_issues = self.scan_for_issues(fix_result.update_type)
            validation_report["issues_remaining"] = len(remaining_issues)
            validation_report["validation_successful"] = len(remaining_issues) == 0
            
            if remaining_issues:
                validation_report["details"]["sample_remaining_issues"] = [
                    asdict(issue) for issue in remaining_issues[:10]  # Show up to 10 samples
                ]
        
        logger.info(f"✅ Validation complete: {validation_report['validation_successful']}, {validation_report['issues_remaining']} issues remaining")
        return validation_report
    
    def create_rollback_snapshot(self, entry_ids: List[str]) -> str:
        """
        Create a rollback snapshot for specific entries before applying fixes.
        
        Args:
            entry_ids: List of entry IDs to snapshot
            
        Returns:
            Path to the snapshot file
        """
        logger.info(f"📸 Creating rollback snapshot for {len(entry_ids)} entries...")
        
        snapshot_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = self.results_dir / f"rollback_snapshot_{snapshot_timestamp}.json"
        
        # Get current data for all entries
        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "entry_count": len(entry_ids),
            "entries": {}
        }
        
        # Process in batches to avoid memory issues
        batch_size = 1000
        for i in range(0, len(entry_ids), batch_size):
            batch_ids = entry_ids[i:i + batch_size]
            
            batch_data = self.db.collection.get(
                ids=batch_ids,
                include=["metadatas", "documents"]
            )
            
            for j, entry_id in enumerate(batch_data['ids']):
                snapshot_data["entries"][entry_id] = {
                    "metadata": batch_data['metadatas'][j],
                    "document": batch_data['documents'][j]
                }
        
        # Save snapshot
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot_data, f, indent=2)
        
        logger.info(f"✅ Rollback snapshot saved: {snapshot_path}")
        return str(snapshot_path)
    
    def apply_rollback(self, snapshot_path: str, dry_run: bool = True) -> UpdateResult:
        """
        Apply rollback from a snapshot file.
        
        Args:
            snapshot_path: Path to the rollback snapshot
            dry_run: If True, only simulate the rollback
            
        Returns:
            UpdateResult with rollback statistics
        """
        logger.info(f"🔄 Applying rollback from {snapshot_path} (dry_run={dry_run})")
        start_time = time.time()
        
        # Load snapshot
        with open(snapshot_path, 'r') as f:
            snapshot_data = json.load(f)
        
        rollback_count = 0
        errors = 0
        
        # Apply rollback in batches
        entries = list(snapshot_data["entries"].items())
        batch_size = 100
        
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            
            try:
                batch_ids = []
                batch_metadatas = []
                batch_documents = []
                
                for entry_id, entry_data in batch:
                    batch_ids.append(entry_id)
                    batch_metadatas.append(entry_data["metadata"])
                    batch_documents.append(entry_data["document"])
                
                if not dry_run:
                    self.db.collection.update(
                        ids=batch_ids,
                        metadatas=batch_metadatas,
                        documents=batch_documents
                    )
                
                rollback_count += len(batch)
                logger.info(f"✅ {'[DRY RUN] ' if dry_run else ''}Rolled back batch {i//batch_size + 1}: {len(batch)} entries")
            
            except Exception as e:
                logger.error(f"Error in rollback batch {i//batch_size + 1}: {e}")
                errors += len(batch)
        
        execution_time = time.time() - start_time
        
        result = UpdateResult(
            update_type="rollback",
            total_scanned=len(entries),
            issues_found=len(entries),
            fixes_applied=rollback_count,
            errors_encountered=errors,
            execution_time_seconds=execution_time,
            dry_run=dry_run,
            timestamp=datetime.now().isoformat(),
            details={"snapshot_path": snapshot_path}
        )
        
        logger.info(f"✅ Rollback complete: {rollback_count} entries, {errors} errors ({execution_time:.2f}s)")
        return result
    
    def _save_scan_results(self, 
                          issue_type: str, 
                          issues: List[ValidationIssue], 
                          total_scanned: int, 
                          scan_time: float):
        """Save scan results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"scan_{issue_type}_{timestamp}.json"
        
        scan_data = {
            "scan_type": issue_type,
            "timestamp": datetime.now().isoformat(),
            "total_scanned": total_scanned,
            "issues_found": len(issues),
            "scan_time_seconds": scan_time,
            "issues": [asdict(issue) for issue in issues]
        }
        
        with open(results_file, 'w') as f:
            json.dump(scan_data, f, indent=2)
        
        logger.info(f"📁 Scan results saved: {results_file}")
    
    def _save_update_result(self, result: UpdateResult):
        """Save update result to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"update_{result.update_type}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        
        logger.info(f"📁 Update result saved: {results_file}")
    
    def get_database_health_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive health report of the database.
        
        Returns:
            Health report with statistics and potential issues
        """
        logger.info("📊 Generating database health report...")
        
        # Get basic stats
        total_entries = self.db.collection.count()
        
        # Sample some entries to check for common issues
        sample_size = min(1000, total_entries)
        sample_data = self.db.collection.get(
            limit=sample_size,
            include=["metadatas"]
        )
        
        # Analyze metadata fields
        field_stats = {}
        enhancement_coverage = {
            'detected_topics': 0,
            'primary_topic': 0,
            'solution_quality_score': 0,
            'validation_strength': 0,
            'outcome_certainty': 0
        }
        
        range_violations = {
            'outcome_certainty': 0,
            'validation_strength': 0,
            'topic_confidence': 0,
            'solution_quality_score': 0
        }
        
        for metadata in sample_data['metadatas']:
            # Count field presence
            for field in enhancement_coverage:
                if field in metadata and metadata[field] != '':
                    enhancement_coverage[field] += 1
            
            # Check range violations
            outcome_certainty = metadata.get('outcome_certainty', 0.0)
            if isinstance(outcome_certainty, (int, float)) and outcome_certainty > 1.0:
                range_violations['outcome_certainty'] += 1
            
            validation_strength = metadata.get('validation_strength', 0.0)
            if isinstance(validation_strength, (int, float)) and abs(validation_strength) > 1.0:
                range_violations['validation_strength'] += 1
            
            topic_confidence = metadata.get('topic_confidence', 0.0)
            if isinstance(topic_confidence, (int, float)) and (topic_confidence < 0.0 or topic_confidence > 2.0):
                range_violations['topic_confidence'] += 1
            
            solution_quality = metadata.get('solution_quality_score', 1.0)
            if isinstance(solution_quality, (int, float)) and (solution_quality < 0.1 or solution_quality > 3.0):
                range_violations['solution_quality_score'] += 1
        
        # Calculate percentages
        for field in enhancement_coverage:
            enhancement_coverage[field] = (enhancement_coverage[field] / sample_size) * 100
        
        for field in range_violations:
            range_violations[field] = (range_violations[field] / sample_size) * 100
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": total_entries,
            "sample_size": sample_size,
            "enhancement_coverage_percent": enhancement_coverage,
            "range_violations_percent": range_violations,
            "health_score": self._calculate_health_score(enhancement_coverage, range_violations),
            "recommendations": self._generate_health_recommendations(range_violations)
        }
        
        logger.info(f"✅ Health report complete - Health Score: {health_report['health_score']:.1f}%")
        return health_report
    
    def _calculate_health_score(self, 
                               enhancement_coverage: Dict[str, float], 
                               range_violations: Dict[str, float]) -> float:
        """Calculate overall database health score (0-100)"""
        
        # Average enhancement coverage (higher is better)
        avg_coverage = sum(enhancement_coverage.values()) / len(enhancement_coverage)
        
        # Average range violations (lower is better)
        avg_violations = sum(range_violations.values()) / len(range_violations)
        
        # Health score: coverage contributes 70%, lack of violations contributes 30%
        health_score = (avg_coverage * 0.7) + ((100 - avg_violations) * 0.3)
        
        return max(0.0, min(100.0, health_score))
    
    def _generate_health_recommendations(self, range_violations: Dict[str, float]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        for field, violation_percent in range_violations.items():
            if violation_percent > 1.0:  # More than 1% violations
                recommendations.append(
                    f"Fix {field} range violations ({violation_percent:.1f}% of entries affected)"
                )
        
        if not recommendations:
            recommendations.append("Database health looks good! No critical issues detected.")
        
        return recommendations


def main():
    """Command-line interface for the incremental updater"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Incremental Database Updater")
    parser.add_argument("--scan-issue", help="Scan for specific issue type")
    parser.add_argument("--fix", help="Apply fix for specific issue type")
    parser.add_argument("--dry-run", action="store_true", help="Simulate fix without applying")
    parser.add_argument("--apply", action="store_true", help="Apply fix (overrides dry-run)")
    parser.add_argument("--health-report", action="store_true", help="Generate health report")
    parser.add_argument("--batch-size", type=int, default=1000, help="Batch size for processing")
    
    args = parser.parse_args()
    
    updater = IncrementalDatabaseUpdater()
    
    if args.health_report:
        report = updater.get_database_health_report()
        print(json.dumps(report, indent=2))
    
    elif args.scan_issue:
        issues = updater.scan_for_issues(args.scan_issue, batch_size=args.batch_size)
        print(f"Found {len(issues)} issues of type '{args.scan_issue}'")
        
        # Show sample issues
        if issues:
            print("\nSample issues:")
            for issue in issues[:5]:
                print(f"  - {issue.entry_id}: {issue.description}")
    
    elif args.fix:
        # First scan for issues
        issues = updater.scan_for_issues(args.fix, batch_size=args.batch_size)
        
        if not issues:
            print(f"No issues found for fix type '{args.fix}'")
            return
        
        # Apply fix
        dry_run = not args.apply
        result = updater.apply_targeted_fix(
            args.fix, 
            issues, 
            dry_run=dry_run, 
            batch_size=args.batch_size
        )
        
        print(f"Fix '{args.fix}' {'simulated' if dry_run else 'applied'}:")
        print(f"  - Issues found: {result.issues_found}")
        print(f"  - Fixes applied: {result.fixes_applied}")
        print(f"  - Errors: {result.errors_encountered}")
        print(f"  - Time: {result.execution_time_seconds:.2f}s")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()