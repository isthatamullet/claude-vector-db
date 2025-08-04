# Database Analysis Methods

Comprehensive methods to analyze the vector database and verify all entries contain complete metadata (basic and enhanced fields).

## 1. **Check Available Analysis Scripts**

First, identify existing metadata analysis tools:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
import os
files = [f for f in os.listdir('.') if 'metadata' in f and 'analy' in f and f.endswith('.py')]
print('Available metadata analysis scripts:')
for f in files: print(f'  {f}')
"
```

## 2. **Comprehensive Metadata Coverage Analysis**

Complete field-by-field coverage analysis:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import json
import logging
logging.basicConfig(level=logging.WARNING)

print('🔍 Comprehensive Metadata Analysis')
print('=' * 50)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'])
total_entries = len(results['metadatas'])

print(f'📊 Total entries: {total_entries:,}')

# Define expected fields
basic_fields = [
    'id', 'type', 'project_name', 'project_path', 'timestamp', 'timestamp_unix',
    'session_id', 'file_name', 'has_code', 'tools_used', 'content_length'
]

enhanced_fields = [
    'detected_topics', 'primary_topic', 'topic_confidence', 'solution_quality_score',
    'is_solution_attempt', 'solution_category', 'has_success_markers', 'has_quality_indicators',
    'previous_message_id', 'next_message_id', 'related_solution_id', 'feedback_message_id',
    'user_feedback_sentiment', 'is_validated_solution', 'is_refuted_attempt',
    'validation_strength', 'outcome_certainty', 'is_feedback_to_solution',
    'message_sequence_position', 'troubleshooting_context_score', 'realtime_learning_boost'
]

print(f'\n📋 Expected Fields:')
print(f'  Basic fields: {len(basic_fields)}')
print(f'  Enhanced fields: {len(enhanced_fields)}')
print(f'  Total expected: {len(basic_fields + enhanced_fields)}')

# Analyze coverage
print(f'\n📈 Field Coverage Analysis:')
field_coverage = {}

for field_list, category in [(basic_fields, 'Basic'), (enhanced_fields, 'Enhanced')]:
    print(f'\n{category} Fields:')
    for field in field_list:
        count = 0
        for metadata in results['metadatas']:
            if field in metadata and metadata[field] is not None and metadata[field] != '':
                count += 1
        
        coverage_pct = (count / total_entries) * 100
        field_coverage[field] = coverage_pct
        
        status = '✅' if coverage_pct > 95 else '⚠️' if coverage_pct > 50 else '❌'
        print(f'  {status} {field}: {count:,}/{total_entries:,} ({coverage_pct:.1f}%)')

# Summary by category
basic_avg = sum(field_coverage[f] for f in basic_fields) / len(basic_fields)
enhanced_avg = sum(field_coverage[f] for f in enhanced_fields) / len(enhanced_fields)

print(f'\n📊 Category Averages:')
print(f'  Basic fields: {basic_avg:.1f}% average coverage')
print(f'  Enhanced fields: {enhanced_avg:.1f}% average coverage')

# Find problematic fields
critical_issues = [f for f in basic_fields if field_coverage[f] < 95]
enhancement_issues = [f for f in enhanced_fields if field_coverage[f] < 50]

print(f'\n🔍 Issues Found:')
if critical_issues:
    print(f'  ❌ Critical (basic fields <95%): {len(critical_issues)}')
    for field in critical_issues:
        print(f'    - {field}: {field_coverage[field]:.1f}%')

if enhancement_issues:
    print(f'  ⚠️ Enhancement gaps (<50%): {len(enhancement_issues)}')
    for field in enhancement_issues:
        print(f'    - {field}: {field_coverage[field]:.1f}%')

if not critical_issues and not enhancement_issues:
    print('  ✅ No critical issues found!')

print(f'\n🎯 Overall Health: {(basic_avg + enhanced_avg) / 2:.1f}%')
"
```

## 3. **Sample Data Quality Check**

Inspect actual data values for quality verification:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import json
import logging
logging.basicConfig(level=logging.WARNING)

print('🔍 Sample Data Quality Check')
print('=' * 40)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'], limit=5)

for i, metadata in enumerate(results['metadatas'][:3]):
    print(f'\n📋 Sample Entry {i+1}:')
    print(f'  ID: {metadata.get(\"id\", \"MISSING\")}')
    print(f'  Type: {metadata.get(\"type\", \"MISSING\")}')
    print(f'  Project: {metadata.get(\"project_name\", \"MISSING\")}')
    print(f'  Timestamp: {metadata.get(\"timestamp\", \"MISSING\")}')
    print(f'  Timestamp Unix: {metadata.get(\"timestamp_unix\", \"MISSING\")}')
    print(f'  Topics: {metadata.get(\"detected_topics\", \"MISSING\")}')
    print(f'  Quality Score: {metadata.get(\"solution_quality_score\", \"MISSING\")}')
    print(f'  Chain Links: prev={metadata.get(\"previous_message_id\", \"MISSING\")}, next={metadata.get(\"next_message_id\", \"MISSING\")}')
"
```

## 4. **Advanced System Health Report**

Run comprehensive system health analysis if available:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
try:
    from unified_enhancement_engine import get_system_health_report
    print('🏥 Advanced System Health Report')
    print('=' * 40)
    health_report = get_system_health_report()
    print(json.dumps(health_report, indent=2))
except ImportError:
    print('⚠️ Advanced health reporting not available')
    print('Try: from mcp_server import get_system_health_report')
except Exception as e:
    print(f'❌ Error running health report: {e}')
"
```

## 5. **Conversation Chain Health Analysis**

Specifically analyze conversation chain relationship fields:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import logging
logging.basicConfig(level=logging.WARNING)

print('🔗 Conversation Chain Analysis')
print('=' * 35)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'])

chain_fields = ['previous_message_id', 'next_message_id', 'related_solution_id', 'feedback_message_id']
total = len(results['metadatas'])

print(f'Total entries: {total:,}')
print('\nChain field population:')

for field in chain_fields:
    populated = sum(1 for m in results['metadatas'] if m.get(field) and m[field] != '')
    print(f'  {field}: {populated:,}/{total:,} ({populated/total*100:.1f}%)')

print(f'\n💡 Note: The system mentioned 1,915 chain relationships were built')
print(f'Expected improvement from recent back-fill processing.')
"
```

## 6. **Enhanced Fields Deep Dive**

Analyze the quality and distribution of enhanced metadata:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import json
import logging
logging.basicConfig(level=logging.WARNING)

print('🧠 Enhanced Fields Deep Analysis')
print('=' * 40)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'])

# Analyze topic detection
topic_entries = [m for m in results['metadatas'] if m.get('detected_topics') and m['detected_topics'] != '{}']
print(f'📊 Topic Detection:')
print(f'  Entries with topics: {len(topic_entries):,}/{len(results[\"metadatas\"]):,} ({len(topic_entries)/len(results[\"metadatas\"])*100:.1f}%)')

if topic_entries:
    # Sample topic analysis
    sample_topics = json.loads(topic_entries[0]['detected_topics']) if topic_entries[0]['detected_topics'] != '{}' else {}
    print(f'  Sample topics: {list(sample_topics.keys())[:5]}')

# Analyze solution quality scores
quality_scores = [float(m.get('solution_quality_score', 1.0)) for m in results['metadatas'] if m.get('solution_quality_score')]
if quality_scores:
    avg_quality = sum(quality_scores) / len(quality_scores)
    high_quality = sum(1 for score in quality_scores if score > 1.5)
    print(f'\n🎯 Solution Quality:')
    print(f'  Average quality score: {avg_quality:.2f}')
    print(f'  High quality solutions (>1.5): {high_quality:,}/{len(quality_scores):,} ({high_quality/len(quality_scores)*100:.1f}%)')

# Analyze validation status
validated = sum(1 for m in results['metadatas'] if m.get('is_validated_solution') == True)
refuted = sum(1 for m in results['metadatas'] if m.get('is_refuted_attempt') == True)

print(f'\n✅ Validation Analysis:')
print(f'  Validated solutions: {validated:,} ({validated/len(results[\"metadatas\"])*100:.2f}%)')
print(f'  Refuted attempts: {refuted:,} ({refuted/len(results[\"metadatas\"])*100:.2f}%)')
"
```

## 7. **Field Population Trends**

Check if recent entries have better metadata coverage:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import logging
logging.basicConfig(level=logging.WARNING)

print('📈 Field Population Trends')
print('=' * 30)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'])

# Sort by timestamp_unix (most recent first)
entries_with_timestamps = [
    (i, m) for i, m in enumerate(results['metadatas']) 
    if m.get('timestamp_unix') and isinstance(m['timestamp_unix'], (int, float))
]

entries_with_timestamps.sort(key=lambda x: x[1]['timestamp_unix'], reverse=True)

recent_entries = entries_with_timestamps[:1000]  # Last 1000 entries
older_entries = entries_with_timestamps[-1000:]  # First 1000 entries

print(f'Comparing recent vs older entries:')
print(f'  Recent entries: {len(recent_entries)}')
print(f'  Older entries: {len(older_entries)}')

# Check key enhanced fields
enhanced_fields = ['detected_topics', 'solution_quality_score', 'previous_message_id', 'troubleshooting_context_score']

for field in enhanced_fields:
    recent_coverage = sum(1 for _, m in recent_entries if m.get(field) and m[field] != '' and m[field] != '{}') / len(recent_entries) * 100
    older_coverage = sum(1 for _, m in older_entries if m.get(field) and m[field] != '' and m[field] != '{}') / len(older_entries) * 100
    
    trend = '📈' if recent_coverage > older_coverage else '📉' if recent_coverage < older_coverage else '➡️'
    print(f'  {trend} {field}: Recent {recent_coverage:.1f}% vs Older {older_coverage:.1f}%')
"
```

## 8. **Export Detailed Report**

Generate a comprehensive analysis report file:

```bash
cd /home/user/.claude-vector-db-enhanced && ./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
import json
import logging
from datetime import datetime
logging.basicConfig(level=logging.WARNING)

print('📄 Generating Detailed Analysis Report')
print('=' * 40)

db = ClaudeVectorDatabase()
results = db.collection.get(include=['metadatas'])
total_entries = len(results['metadatas'])

report = {
    'analysis_date': datetime.now().isoformat(),
    'total_entries': total_entries,
    'field_coverage': {},
    'sample_entries': results['metadatas'][:3],
    'summary': {}
}

# All expected fields
all_fields = [
    'id', 'type', 'project_name', 'project_path', 'timestamp', 'timestamp_unix',
    'session_id', 'file_name', 'has_code', 'tools_used', 'content_length',
    'detected_topics', 'primary_topic', 'topic_confidence', 'solution_quality_score',
    'is_solution_attempt', 'solution_category', 'has_success_markers', 'has_quality_indicators',
    'previous_message_id', 'next_message_id', 'related_solution_id', 'feedback_message_id',
    'user_feedback_sentiment', 'is_validated_solution', 'is_refuted_attempt',
    'validation_strength', 'outcome_certainty', 'is_feedback_to_solution',
    'message_sequence_position', 'troubleshooting_context_score', 'realtime_learning_boost'
]

# Calculate coverage for each field
for field in all_fields:
    count = sum(1 for m in results['metadatas'] if field in m and m[field] is not None and m[field] != '')
    report['field_coverage'][field] = {
        'count': count,
        'percentage': (count / total_entries) * 100
    }

# Summary statistics
basic_fields = all_fields[:11]
enhanced_fields = all_fields[11:]

basic_avg = sum(report['field_coverage'][f]['percentage'] for f in basic_fields) / len(basic_fields)
enhanced_avg = sum(report['field_coverage'][f]['percentage'] for f in enhanced_fields) / len(enhanced_fields)

report['summary'] = {
    'basic_fields_average': basic_avg,
    'enhanced_fields_average': enhanced_avg,
    'overall_health': (basic_avg + enhanced_avg) / 2,
    'critical_issues': [f for f in basic_fields if report['field_coverage'][f]['percentage'] < 95],
    'enhancement_gaps': [f for f in enhanced_fields if report['field_coverage'][f]['percentage'] < 50]
}

# Save report
with open('database_analysis_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f'✅ Report saved to database_analysis_report.json')
print(f'📊 Overall health: {report[\"summary\"][\"overall_health\"]:.1f}%')
print(f'❌ Critical issues: {len(report[\"summary\"][\"critical_issues\"])}')
print(f'⚠️ Enhancement gaps: {len(report[\"summary\"][\"enhancement_gaps\"])}')
"
```

## Usage Notes

- **Run in order**: Start with #2 (Comprehensive Analysis) for overall health
- **Check samples**: Use #3 to verify data quality
- **Chain analysis**: Use #5 if conversation chains are important  
- **Performance**: Large databases may take 30-60 seconds for full analysis
- **Output**: All commands provide immediate console output
- **Reports**: Use #8 to generate exportable JSON reports

## Expected Results

Based on recent system improvements:
- **Basic fields**: Should show 95-100% coverage
- **Enhanced fields**: May show mixed coverage (normal for advanced features)
- **Conversation chains**: Should show improvement from recent back-fill processing
- **Overall health**: Target 70-80% for production-ready system