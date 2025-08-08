#!/usr/bin/env python3
"""Enable hybrid processing in Claude Code hooks"""

import re

# Update response hook
hook_files = [
    '/home/user/.claude/hooks/index-claude-response.py',
    '/home/user/.claude/hooks/index-user-prompt.py'
]

for hook_file in hook_files:
    try:
        with open(hook_file, 'r') as f:
            content = f.read()
        
        # Add hybrid enablement if not present
        if 'enable_hybrid=True' not in content:
            # Find UnifiedEnhancementProcessor initialization
            pattern = r'(UnifiedEnhancementProcessor\([^)]*)\)'
            replacement = r'\1, enable_hybrid=True)'
            content = re.sub(pattern, replacement, content)
            
            with open(hook_file, 'w') as f:
                f.write(content)
            
            print(f"✅ Enabled hybrid processing in {hook_file}")
        else:
            print(f"✅ Hybrid already enabled in {hook_file}")
            
    except FileNotFoundError:
        print(f"⚠️ Hook file not found: {hook_file}")
    except Exception as e:
        print(f"❌ Error updating {hook_file}: {e}")

print("✅ Hybrid processing enabled in hooks")