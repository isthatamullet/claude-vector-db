#!/usr/bin/env python3
"""
Claude Code Vector Database CLI Tool
Command-line interface for searching conversation history
"""

import argparse
import requests
import sys
from typing import Optional

# Default API configuration
DEFAULT_API_URL = "http://localhost:8000"

def search_conversations(query: str, 
                        project: Optional[str] = None,
                        limit: int = 5,
                        api_url: str = DEFAULT_API_URL) -> dict:
    """Search conversations via API"""
    
    try:
        params = {
            'q': query,
            'limit': limit,
            'metadata': True
        }
        
        if project:
            params['project'] = project
        
        response = requests.get(f"{api_url}/search", params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print(f"   Make sure the server is running at {api_url}")
        print("   Start it with: ./start_server.sh")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("❌ Error: API request timed out")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: API request failed: {e}")
        sys.exit(1)

def get_database_stats(api_url: str = DEFAULT_API_URL) -> dict:
    """Get database statistics"""
    
    try:
        response = requests.get(f"{api_url}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting database stats: {e}")
        return {}

def get_available_projects(api_url: str = DEFAULT_API_URL) -> dict:
    """Get available projects"""
    
    try:
        response = requests.get(f"{api_url}/projects", timeout=10)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting projects: {e}")
        return {}

def rebuild_database(api_url: str = DEFAULT_API_URL, max_files: Optional[int] = None) -> dict:
    """Rebuild database index"""
    
    try:
        params = {}
        if max_files:
            params['max_files'] = max_files
            
        print("🔄 Rebuilding database index... (this may take several minutes)")
        response = requests.post(f"{api_url}/rebuild", params=params, timeout=300)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        print("⏰ Database rebuild timed out - it may still be processing")
        return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error rebuilding database: {e}")
        return {}

def format_search_results(results: dict, show_details: bool = False):
    """Format and display search results"""
    
    if not results.get('results'):
        print("🔍 No results found")
        return
    
    query = results.get('query', '')
    project = results.get('current_project')
    total = results.get('total_found', 0)
    search_time = results.get('search_time_ms', 0)
    
    print(f"\n🔍 Search: '{query}'")
    if project:
        print(f"📁 Project: {project}")
    print(f"📊 Found {total} results in {search_time:.1f}ms")
    print("=" * 60)
    
    for i, result in enumerate(results['results'], 1):
        score = result.get('relevance_score', 0)
        project_name = result.get('project_name', 'unknown')
        msg_type = result.get('type', 'unknown')
        has_code = result.get('has_code', False)
        tools_used = result.get('tools_used', [])
        
        print(f"\n{i}. [{msg_type}] {project_name} (score: {score:.3f})")
        
        if has_code:
            print("   💻 Contains code")
        
        if tools_used:
            print(f"   🔧 Tools: {', '.join(tools_used[:3])}")
        
        # Show content preview
        content = result.get('content', '')
        preview = content[:200] + "..." if len(content) > 200 else content
        print(f"   {preview}")
        
        if show_details:
            print(f"   📄 File: {result.get('file_name', 'unknown')}")
            print(f"   🕒 Time: {result.get('timestamp', 'unknown')}")
            print(f"   🆔 ID: {result.get('id', 'unknown')}")
        
        print("-" * 60)

def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Claude Code Vector Database CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  claude_search.py "React hooks error"
  claude_search.py "performance optimization" --project tylergohr.com
  claude_search.py "TypeScript interface" --limit 10 --details
  claude_search.py --stats
  claude_search.py --projects
  claude_search.py --rebuild
        """
    )
    
    # Main actions
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--projects', action='store_true', help='List available projects')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild database index')
    
    # Search options
    parser.add_argument('--project', '-p', help='Current project name for relevance boosting')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--details', '-d', action='store_true', help='Show detailed result information')
    
    # Server options
    parser.add_argument('--api-url', default=DEFAULT_API_URL, help=f'API server URL (default: {DEFAULT_API_URL})')
    parser.add_argument('--max-files', type=int, help='Maximum files to process during rebuild')
    
    args = parser.parse_args()
    
    # Handle special actions
    if args.stats:
        print("📊 Database Statistics")
        print("=" * 40)
        stats = get_database_stats(args.api_url)
        
        if stats:
            print(f"Total entries: {stats.get('total_entries', 0)}")
            print(f"Code entries: {stats.get('code_entries', 0)} ({stats.get('code_percentage', 0):.1f}%)")
            print(f"Message types: {stats.get('message_types', {})}")
            
            projects = stats.get('projects', {})
            if projects:
                print(f"\nProjects ({len(projects)}):")
                for project, data in sorted(projects.items(), key=lambda x: x[1].get('count', 0), reverse=True)[:10]:
                    count = data.get('count', 0)
                    user_msgs = data.get('user', 0)
                    assistant_msgs = data.get('assistant', 0)
                    print(f"  {project}: {count} entries ({user_msgs} user, {assistant_msgs} assistant)")
        
        return
    
    if args.projects:
        print("📁 Available Projects")
        print("=" * 40)
        projects_data = get_available_projects(args.api_url)
        
        if projects_data and 'projects' in projects_data:
            for project in projects_data['projects']:
                name = project.get('name', 'unknown')
                entries = project.get('entries', 0)
                code_entries = project.get('code_entries', 0)
                print(f"  {name}: {entries} entries ({code_entries} with code)")
        
        return
    
    if args.rebuild:
        print("🔄 Rebuilding Database Index")
        print("=" * 40)
        result = rebuild_database(args.api_url, args.max_files)
        
        if result:
            if result.get('success'):
                print(f"✅ {result.get('message', 'Rebuild completed')}")
                print(f"📊 Processed: {result.get('total_processed', 0)} entries")
                
                rebuild_results = result.get('rebuild_results', {})
                if rebuild_results:
                    print(f"   Added: {rebuild_results.get('added', 0)}")
                    print(f"   Skipped: {rebuild_results.get('skipped', 0)}")
                    print(f"   Errors: {rebuild_results.get('errors', 0)}")
            else:
                print(f"❌ Rebuild failed: {result}")
        
        return
    
    # Main search functionality
    if not args.query:
        parser.print_help()
        print("\n💡 Tip: Use --stats to see database information or --projects to list available projects")
        return
    
    # Perform search
    results = search_conversations(
        query=args.query,
        project=args.project,
        limit=args.limit,
        api_url=args.api_url
    )
    
    # Display results
    format_search_results(results, show_details=args.details)

if __name__ == "__main__":
    main()