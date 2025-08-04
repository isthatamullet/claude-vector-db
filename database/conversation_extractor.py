#!/usr/bin/env python3
"""
Enhanced Claude Code Conversation Data Extractor
Extracts and processes conversation data from .claude/projects/*.jsonl files
with advanced context awareness, topic detection, quality scoring, and feedback learning.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import logging

# Enhanced context awareness imports
from database.enhanced_conversation_entry import ConversationEntry, EnhancedConversationEntry, create_enhanced_entry_from_dict
# Import from enhanced_context package
from database.enhanced_context import (
    detect_conversation_topics,
    calculate_solution_quality_score,
    analyze_conversation_adjacency,
    analyze_feedback_sentiment,
    apply_feedback_to_solution
)

# Import real-time learning functions from the standalone enhanced_context.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
exec(open('/home/user/.claude-vector-db-enhanced/database/enhanced_context.py').read())

# Now process_conversation_for_realtime_learning and get_realtime_learning_boost are available

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationExtractor:
    """Extract and process Claude conversation data for vector indexing"""
    
    def __init__(self, claude_projects_dir: str = "/home/user/.claude/projects"):
        self.claude_projects_dir = Path(claude_projects_dir)
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'been', 'be', 
            'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may', 
            'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
    
    def convert_timestamp_to_unix(self, timestamp_str: str) -> Optional[float]:
        """Convert ISO timestamp string to Unix timestamp"""
        try:
            # Handle Z suffix (UTC timezone)
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            
            dt = datetime.fromisoformat(timestamp_str)
            return dt.timestamp()
            
        except Exception as e:
            logger.warning(f"Failed to convert timestamp '{timestamp_str}': {e}")
            return None
        
    def extract_project_name(self, project_path: str) -> str:
        """Extract clean project name from path"""
        if project_path == 'unknown':
            return 'unknown'
        
        path = Path(project_path)
        return path.name
    
    def extract_tools_from_content(self, content: str) -> List[str]:
        """Extract tool names from conversation content"""
        tools = []
        
        # Look for common Claude Code tool patterns
        tool_patterns = [
            r'<function_calls>.*?<invoke name="([^"]+)"',
            r'tool_name["\']:\s*["\']([^"\']+)["\']',
            r'Using tool:\s*([^\s\n]+)',
        ]
        
        for pattern in tool_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            tools.extend(matches)
        
        # Remove duplicates and clean
        return list(set([tool.strip() for tool in tools if tool.strip()]))
    
    def has_code_content(self, content: str) -> bool:
        """Check if content contains code snippets"""
        code_indicators = [
            '```', 'function', 'class ', 'def ', 'import ', 'const ', 'let ', 
            'var ', 'npm ', 'git ', 'cd ', 'mkdir', '#!/', 'python', 'node',
            'react', 'typescript', 'javascript', 'css', 'html', 'sql'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in code_indicators)
    
    def clean_content(self, content: Any) -> str:
        """Clean and extract meaningful text content"""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            # Handle complex content structures (tool results, etc.)
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if 'content' in item:
                        text_parts.append(str(item['content']))
                    elif 'text' in item:
                        text_parts.append(str(item['text']))
                    else:
                        # Extract any string values
                        for key, value in item.items():
                            if isinstance(value, str):  
                                text_parts.append(value)
                elif isinstance(item, str):
                    text_parts.append(item)
            text = ' '.join(text_parts)
        else:
            text = str(content)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\/]', ' ', text)  # Remove special chars but keep basic punctuation
        text = text.strip()
        
        return text
    
    def generate_entry_id(self, entry: Dict, line_num: int, file_path: Path = None) -> str:
        """Generate unique entry ID from entry data and line number"""
        msg_type = entry.get('type', 'unknown')
        file_stem = file_path.stem if file_path else 'unknown'
        return f"{file_stem}_{line_num}_{msg_type}"
    
    def detect_code_patterns(self, content: str) -> bool:
        """Detect if content contains code patterns - alias for has_code_content"""
        return self.has_code_content(content)
    
    def extract_tools_used(self, entry: Dict) -> List[str]:
        """Extract tools used from entry - alias for extract_tools_from_content"""
        content = str(entry.get('message', {}).get('content', ''))
        return self.extract_tools_from_content(content)
    
    def extract_from_jsonl_file(self, file_path: Path, max_entries: int = None) -> Generator[ConversationEntry, None, None]:
        """Extract conversation entries from a single JSONL file"""
        
        logger.info(f"Processing {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return
        
        processed_count = 0
        session_id = None
        
        for line_num, line in enumerate(lines, 1):
            if max_entries and processed_count >= max_entries:
                break
                
            line = line.strip()
            if not line:
                continue
                
            try:
                entry = json.loads(line)
                
                # Skip meta messages
                if entry.get('isMeta'):
                    continue
                
                # Extract core data
                message = entry.get('message', {})
                content = message.get('content', '')
                msg_type = entry.get('type', 'unknown')
                project_path = entry.get('cwd', 'unknown')
                timestamp = entry.get('timestamp', '')
                
                # Extract session ID if available
                if not session_id:
                    session_id = entry.get('sessionId', file_path.stem)
                
                # Clean and validate content
                cleaned_content = self.clean_content(content)
                
                # Skip entries with insufficient content
                if len(cleaned_content) < 20:
                    continue
                
                # Limit content length for efficiency
                if len(cleaned_content) > 8000:
                    cleaned_content = cleaned_content[:8000] + "..."
                
                # Extract metadata
                project_name = self.extract_project_name(project_path)
                tools_used = self.extract_tools_from_content(str(content))
                has_code = self.has_code_content(cleaned_content)
                
                # Convert timestamp to Unix format for fast filtering
                timestamp_unix = self.convert_timestamp_to_unix(timestamp)
                
                # Create structured entry
                entry_id = f"{file_path.stem}_{line_num}_{msg_type}"
                
                conversation_entry = ConversationEntry(
                    id=entry_id,
                    content=cleaned_content,
                    type=msg_type,
                    project_path=project_path,
                    project_name=project_name,
                    timestamp=timestamp,
                    timestamp_unix=timestamp_unix,
                    session_id=session_id,
                    file_name=file_path.name,
                    has_code=has_code,
                    tools_used=tools_used,
                    content_length=len(cleaned_content)
                )
                
                yield conversation_entry
                processed_count += 1
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON error in {file_path.name} line {line_num}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Processing error in {file_path.name} line {line_num}: {e}")
                continue
        
        logger.info(f"✅ Extracted {processed_count} entries from {file_path.name}")
    
    def extract_all_conversations(self, max_files: int = None) -> List[ConversationEntry]:
        """Extract all conversations from Claude projects directory"""
        
        if not self.claude_projects_dir.exists():
            logger.error(f"Claude projects directory not found: {self.claude_projects_dir}")
            return []
        
        # Find all JSONL files
        jsonl_files = list(self.claude_projects_dir.rglob("*.jsonl"))
        
        if max_files:
            jsonl_files = jsonl_files[:max_files]
        
        logger.info(f"Found {len(jsonl_files)} conversation files to process")
        
        all_entries = []
        
        for file_path in jsonl_files:
            entries = list(self.extract_from_jsonl_file(file_path))
            all_entries.extend(entries)
        
        logger.info(f"✅ Total extracted: {len(all_entries)} conversation entries")
        
        # Sort by timestamp for consistent ordering
        all_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return all_entries
    
    def get_project_statistics(self, entries: List[ConversationEntry]) -> Dict[str, Any]:
        """Get statistics about extracted conversations"""
        
        if not entries:
            return {}
        
        projects = {}
        total_content_length = 0
        tools_usage = {}
        code_entries = 0
        
        for entry in entries:
            # Project stats
            if entry.project_name not in projects:
                projects[entry.project_name] = {
                    'count': 0,
                    'user_messages': 0,
                    'assistant_messages': 0,
                    'has_code': 0,
                    'tools_used': set()
                }
            
            projects[entry.project_name]['count'] += 1
            projects[entry.project_name][f'{entry.type}_messages'] += 1
            
            if entry.has_code:
                projects[entry.project_name]['has_code'] += 1
                code_entries += 1
            
            # Tools stats
            for tool in entry.tools_used:
                projects[entry.project_name]['tools_used'].add(tool)
                tools_usage[tool] = tools_usage.get(tool, 0) + 1
            
            total_content_length += entry.content_length
        
        # Convert sets to lists for JSON serialization
        for project_data in projects.values():
            project_data['tools_used'] = list(project_data['tools_used'])
        
        return {
            'total_entries': len(entries),
            'total_projects': len(projects),
            'average_content_length': total_content_length // len(entries) if entries else 0,
            'code_entries': code_entries,
            'code_percentage': (code_entries / len(entries)) * 100 if entries else 0,
            'projects': projects,
            'top_tools': sorted(tools_usage.items(), key=lambda x: x[1], reverse=True)[:10],
            'timestamp_range': {
                'earliest': min(entry.timestamp for entry in entries) if entries else None,
                'latest': max(entry.timestamp for entry in entries) if entries else None
            }
        }
    
    # Enhanced processing methods
    
    def extract_with_enhancements(self, file_path: Path, max_entries: int = None) -> Generator[EnhancedConversationEntry, None, None]:
        """
        Extract conversation entries with full enhancement processing.
        
        Applies topic detection, quality scoring, adjacency analysis, and feedback learning
        to create EnhancedConversationEntry objects with comprehensive metadata.
        
        Args:
            file_path: Path to JSONL conversation file
            max_entries: Maximum entries to process (for testing)
            
        Yields:
            EnhancedConversationEntry objects with full enhancement analysis
        """
        logger.info(f"🔍 Processing with enhancements: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return
        
        # Parse all messages first for adjacency analysis
        messages = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                entry = json.loads(line)
                if entry.get('isMeta'):
                    continue
                    
                # Extract basic message data
                message = entry.get('message', {})
                content = message.get('content', '')
                cleaned_content = self.clean_content(content)
                
                if len(cleaned_content) < 20:
                    continue
                    
                # Create message dict for adjacency analysis
                msg_dict = {
                    'id': self.generate_entry_id(entry, line_num, file_path),
                    'content': cleaned_content,
                    'type': entry.get('type', 'unknown'),
                    'timestamp': entry.get('timestamp', ''),
                    'raw_entry': entry,
                    'line_num': line_num
                }
                messages.append(msg_dict)
                
            except json.JSONDecodeError:
                continue
        
        # Perform adjacency analysis on all messages
        enhanced_messages, conversation_context = analyze_conversation_adjacency(messages)
        
        processed_count = 0
        session_id = None
        
        for enhanced_msg in enhanced_messages:
            if max_entries and processed_count >= max_entries:
                break
                
            try:
                entry = enhanced_msg['raw_entry']
                
                # Extract metadata
                if not session_id:
                    session_id = entry.get('sessionId', file_path.stem)
                
                project_path = entry.get('cwd', 'unknown')
                project_name = self.extract_project_name(project_path)
                timestamp = entry.get('timestamp', '')
                timestamp_unix = self.convert_timestamp_to_unix(timestamp)
                
                # Code and tool detection
                has_code = self.detect_code_patterns(enhanced_msg['content'])
                tools_used = self.extract_tools_used(entry)
                
                # Create base metadata
                metadata = {
                    'id': enhanced_msg['id'],
                    'content': enhanced_msg['content'],
                    'type': enhanced_msg['type'],
                    'project_path': project_path,
                    'project_name': project_name,
                    'timestamp': timestamp,
                    'timestamp_unix': timestamp_unix,
                    'session_id': session_id,
                    'file_name': file_path.name,
                    'has_code': has_code,
                    'tools_used': tools_used,
                    'content_length': len(enhanced_msg['content'])
                }
                
                # Apply topic detection
                detected_topics = detect_conversation_topics(enhanced_msg['content'])
                
                # Apply quality scoring
                quality_score = calculate_solution_quality_score(enhanced_msg['content'], metadata)
                
                # Create enhancement fields
                enhancement_fields = {
                    'detected_topics': detected_topics,
                    'primary_topic': max(detected_topics.items(), key=lambda x: x[1])[0] if detected_topics else None,
                    'topic_confidence': max(detected_topics.values()) if detected_topics else 0.0,
                    'solution_quality_score': quality_score,
                    'has_success_markers': quality_score > 1.5,
                    'has_quality_indicators': quality_score > 2.0,
                    'previous_message_id': enhanced_msg.get('previous_message_id'),
                    'next_message_id': enhanced_msg.get('next_message_id'),
                    'message_sequence_position': enhanced_msg.get('message_sequence_position', 0),
                    'is_solution_attempt': enhanced_msg.get('is_solution_attempt', False),
                    'solution_category': enhanced_msg.get('solution_category'),
                    'feedback_message_id': enhanced_msg.get('feedback_message_id'),
                    'is_feedback_to_solution': enhanced_msg.get('is_feedback_to_solution', False),
                    'related_solution_id': enhanced_msg.get('related_solution_id')
                }
                
                # Apply feedback learning if this is feedback to a solution
                if enhanced_msg.get('is_feedback_to_solution', False):
                    feedback_analysis = analyze_feedback_sentiment(enhanced_msg['content'])
                    enhancement_fields.update({
                        'user_feedback_sentiment': feedback_analysis['sentiment'],
                        'validation_strength': feedback_analysis['strength'] * feedback_analysis['confidence'],
                        'outcome_certainty': feedback_analysis['certainty']
                    })
                
                # Create enhanced conversation entry
                enhanced_entry = create_enhanced_entry_from_dict(metadata, **enhancement_fields)
                
                yield enhanced_entry
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"Enhancement processing error in {file_path.name} line {enhanced_msg['line_num']}: {e}")
                continue
        
        logger.info(f"✅ Enhanced processing complete: {processed_count} entries from {file_path.name}")
    
    def extract_all_enhanced_conversations(self, max_files: int = None) -> List[EnhancedConversationEntry]:
        """
        Extract all conversations with full enhancement processing.
        
        Args:
            max_files: Maximum number of files to process
            
        Returns:
            List of EnhancedConversationEntry objects with comprehensive analysis
        """
        if not self.claude_projects_dir.exists():
            logger.error(f"Claude projects directory not found: {self.claude_projects_dir}")
            return []
        
        # Find all JSONL files
        jsonl_files = list(self.claude_projects_dir.rglob("*.jsonl"))
        
        if max_files:
            jsonl_files = jsonl_files[:max_files]
        
        logger.info(f"🔍 Found {len(jsonl_files)} conversation files for enhanced processing")
        
        all_enhanced_entries = []
        
        for file_path in jsonl_files:
            try:
                entries = list(self.extract_with_enhancements(file_path))
                all_enhanced_entries.extend(entries)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue
        
        # Apply cross-conversation feedback learning
        if all_enhanced_entries:
            all_enhanced_entries = self.apply_cross_conversation_learning(all_enhanced_entries)
        
        logger.info(f"✅ Total enhanced entries extracted: {len(all_enhanced_entries)}")
        
        # Sort by timestamp for consistent ordering
        all_enhanced_entries.sort(key=lambda x: x.timestamp, reverse=True)
        
        return all_enhanced_entries
    
    def apply_cross_conversation_learning(self, entries: List[EnhancedConversationEntry]) -> List[EnhancedConversationEntry]:
        """
        Apply cross-conversation feedback learning to update solution validation status.
        
        Links solutions to feedback across the entire conversation dataset to improve
        validation accuracy and learning from user feedback patterns.
        
        Args:
            entries: List of enhanced conversation entries
            
        Returns:
            Updated entries with cross-conversation learning applied
        """
        logger.info("🧠 Applying cross-conversation feedback learning...")
        
        # Group entries by conversation/session
        sessions = {}
        for entry in entries:
            session_key = f"{entry.session_id}_{entry.file_name}"
            if session_key not in sessions:
                sessions[session_key] = []
            sessions[session_key].append(entry)
        
        # Apply feedback learning within each session + Real-time Feedback Loop Learning
        updated_entries = []
        learning_stats = {'sessions_processed': 0, 'solutions_updated': 0, 'feedback_applied': 0, 'realtime_loops_detected': 0}
        realtime_learning_results = []
        
        for session_key, session_entries in sessions.items():
            # Sort by sequence position
            session_entries.sort(key=lambda x: x.message_sequence_position)
            
            # ✨ REAL-TIME FEEDBACK LOOP LEARNING ✨
            # Convert enhanced entries to message format for real-time processing
            session_messages = [{
                'id': entry.id,
                'type': entry.type,
                'content': entry.content,
                'timestamp': entry.timestamp,
                'session_id': entry.session_id
            } for entry in session_entries]
            
            # Process conversation for real-time feedback loops
            try:
                realtime_result = process_conversation_for_realtime_learning(session_messages)
                realtime_learning_results.append(realtime_result)
                learning_stats['realtime_loops_detected'] += realtime_result['feedback_loops_detected']
                
                if realtime_result['real_time_learning_applied']:
                    logger.info(f"🔄 Real-time learning applied to session {session_key}: "
                               f"{realtime_result['feedback_loops_detected']} feedback loops detected")
            except Exception as e:
                logger.warning(f"Real-time learning failed for session {session_key}: {e}")
            
            # Apply feedback to solutions within this session
            for i, entry in enumerate(session_entries):
                if entry.feedback_message_id:
                    # Find the feedback message
                    feedback_entry = next(
                        (e for e in session_entries if e.id == entry.feedback_message_id), 
                        None
                    )
                    
                    if feedback_entry and feedback_entry.user_feedback_sentiment:
                        # Apply feedback to solution
                        entry_dict = entry.__dict__.copy()
                        feedback_analysis = {
                            'sentiment': feedback_entry.user_feedback_sentiment,
                            'strength': abs(feedback_entry.validation_strength),
                            'confidence': 0.8,  # Default confidence for cross-conversation
                            'certainty': feedback_entry.outcome_certainty
                        }
                        
                        updated_dict = apply_feedback_to_solution(entry_dict, feedback_analysis)
                        
                        # Update entry fields
                        entry.is_validated_solution = updated_dict.get('is_validated_solution', False)
                        entry.is_refuted_attempt = updated_dict.get('is_refuted_attempt', False)
                        entry.validation_strength = updated_dict.get('validation_strength', 0.0)
                        entry.user_feedback_sentiment = updated_dict.get('user_feedback_sentiment')
                        entry.outcome_certainty = updated_dict.get('outcome_certainty', 0.0)
                        
                        learning_stats['solutions_updated'] += 1
                        learning_stats['feedback_applied'] += 1
            
            updated_entries.extend(session_entries)
            learning_stats['sessions_processed'] += 1
        
        # Log comprehensive learning results
        total_realtime_feedback_loops = sum(result['feedback_loops_detected'] for result in realtime_learning_results)
        logger.info(f"✅ Cross-conversation + Real-time learning complete: {learning_stats}")
        logger.info(f"🔄 Real-time feedback loop learning: {total_realtime_feedback_loops} loops processed across {len(realtime_learning_results)} sessions")
        
        # Store real-time learning results for inspection
        if hasattr(self, '_last_realtime_results'):
            self._last_realtime_results = realtime_learning_results
        
        return updated_entries
    
    def get_enhanced_statistics(self, entries: List[EnhancedConversationEntry]) -> Dict[str, Any]:
        """
        Generate comprehensive statistics for enhanced conversation entries.
        
        Args:
            entries: List of enhanced conversation entries
            
        Returns:
            Detailed statistics including enhancement metadata
        """
        if not entries:
            return {}
        
        # Basic statistics
        basic_stats = self.get_project_statistics([entry for entry in entries])
        
        # Enhancement-specific statistics
        topics_detected = sum(1 for entry in entries if entry.detected_topics)
        solutions_identified = sum(1 for entry in entries if entry.is_solution_attempt)
        validated_solutions = sum(1 for entry in entries if entry.is_validated_solution)
        refuted_solutions = sum(1 for entry in entries if entry.is_refuted_attempt)
        
        # Topic distribution
        all_topics = {}
        for entry in entries:
            for topic, score in entry.detected_topics.items():
                if topic not in all_topics:
                    all_topics[topic] = []
                all_topics[topic].append(score)
        
        topic_stats = {
            topic: {
                'count': len(scores),
                'avg_score': sum(scores) / len(scores),
                'max_score': max(scores)
            }
            for topic, scores in all_topics.items()
        }
        
        # Quality distribution
        quality_scores = [entry.solution_quality_score for entry in entries if entry.solution_quality_score > 1.0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 1.0
        
        # Validation statistics
        feedback_coverage = sum(1 for entry in entries if entry.user_feedback_sentiment) / max(solutions_identified, 1)
        
        enhancement_stats = {
            'enhancement_coverage': {
                'topics_detected': topics_detected,
                'topics_percentage': (topics_detected / len(entries)) * 100,
                'solutions_identified': solutions_identified,
                'solutions_percentage': (solutions_identified / len(entries)) * 100
            },
            'solution_validation': {
                'total_solutions': solutions_identified,
                'validated_solutions': validated_solutions,
                'refuted_solutions': refuted_solutions,
                'validation_rate': validated_solutions / max(solutions_identified, 1),
                'refutation_rate': refuted_solutions / max(solutions_identified, 1),
                'feedback_coverage': feedback_coverage
            },
            'topic_analysis': {
                'unique_topics': len(all_topics),
                'most_common_topics': sorted(topic_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10],
                'highest_scoring_topics': sorted(topic_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)[:5]
            },
            'quality_metrics': {
                'average_quality_score': avg_quality,
                'high_quality_solutions': sum(1 for score in quality_scores if score > 2.0),
                'quality_distribution': {
                    'low': sum(1 for score in quality_scores if 1.0 <= score < 1.5),
                    'medium': sum(1 for score in quality_scores if 1.5 <= score < 2.0),
                    'high': sum(1 for score in quality_scores if score >= 2.0)
                }
            }
        }
        
        # Combine basic and enhancement statistics
        basic_stats.update({'enhancement_analysis': enhancement_stats})
        
        return basic_stats

def main():
    """Test the conversation extractor"""
    
    extractor = ConversationExtractor()
    
    # Extract sample conversations for testing
    print("🔍 Extracting conversations from Claude projects...")
    entries = extractor.extract_all_conversations(max_files=5)  # Test with 5 files
    
    if not entries:
        print("❌ No conversation entries found")
        return
    
    # Show statistics
    stats = extractor.get_project_statistics(entries)
    
    print("\n📊 Extraction Statistics:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Projects: {stats['total_projects']}")
    print(f"   Average content length: {stats['average_content_length']} chars")
    print(f"   Code entries: {stats['code_entries']} ({stats['code_percentage']:.1f}%)")
    
    print("\n🔧 Top tools used:")
    for tool, count in stats['top_tools'][:5]:
        print(f"   {tool}: {count} times")
    
    print("\n📁 Project breakdown:")
    for project, data in list(stats['projects'].items())[:5]:
        print(f"   {project}: {data['count']} entries ({data['user_messages']} user, {data['assistant_messages']} assistant)")
    
    # Show sample entries
    print("\n📝 Sample conversation entries:")
    for i, entry in enumerate(entries[:3]):
        print(f"\n{i+1}. [{entry.type}] {entry.project_name}")
        print(f"   ID: {entry.id}")
        print(f"   Tools: {entry.tools_used}")
        print(f"   Content: {entry.content[:150]}...")
    
    print("\n✅ Conversation extraction test completed!")

if __name__ == "__main__":
    main()