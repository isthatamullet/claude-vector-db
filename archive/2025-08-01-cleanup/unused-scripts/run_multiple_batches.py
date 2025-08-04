#!/usr/bin/env python3
"""
Multiple Batch Runner for Enhanced Conversation Sync

This script runs multiple batches automatically with safe timeouts,
useful for processing more files in a single Claude Code session
while staying within timeout limits.
"""

import subprocess
import sys
import time
from pathlib import Path

def run_batch(batch_size: int = 4, max_batches: int = 5):
    """Run multiple batches with timeout safety"""
    
    print("🚀 Starting multiple batch processing")
    print(f"📊 Target: {max_batches} batches of {batch_size} files each")
    print("⏱️  Safe timeout: ~90 seconds per batch")
    
    batch_script = Path(__file__).parent / "run_enhanced_batch_sync.py"
    python_exe = Path(__file__).parent / "venv" / "bin" / "python"
    
    successful_batches = 0
    
    for batch_num in range(1, max_batches + 1):
        print(f"\n📦 Starting batch {batch_num}/{max_batches}")
        start_time = time.time()
        
        try:
            # Run batch with 90 second timeout (safe margin under 2 minutes)
            result = subprocess.run([
                str(python_exe), 
                str(batch_script), 
                f"--batch-size={batch_size}"
            ], timeout=90, capture_output=True, text=True)
            
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Batch {batch_num} completed successfully in {elapsed:.1f}s")
                successful_batches += 1
                
                # Check if we're done by parsing output
                if "BATCH SYNC COMPLETE!" in result.stdout:
                    print(f"🎉 All files processed! Completed in {batch_num} batches.")
                    break
                    
            else:
                print(f"❌ Batch {batch_num} failed:")
                print(result.stderr)
                break
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  Batch {batch_num} timed out after 90 seconds - batch size too large")
            print(f"💡 Suggestion: Try smaller batch size (current: {batch_size})")
            break
            
        except Exception as e:
            print(f"❌ Error running batch {batch_num}: {e}")
            break
    
    # Final status
    print("\n📈 Multiple Batch Summary:")
    print(f"  Successful batches: {successful_batches}/{batch_num}")
    
    # Show final progress
    try:
        result = subprocess.run([
            str(python_exe), 
            str(batch_script), 
            "--stats"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"\n{result.stdout}")
        
    except Exception:
        print("Could not retrieve final statistics")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run multiple enhanced batch syncs automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_multiple_batches.py                    # 5 batches of 4 files each
  python run_multiple_batches.py --batches 3        # 3 batches
  python run_multiple_batches.py --batch-size 3     # Smaller batch size
  python run_multiple_batches.py --batches 10 --batch-size 2  # Many small batches
        """
    )
    
    parser.add_argument(
        '--batches', 
        type=int, 
        default=5, 
        help='Maximum number of batches to run (default: 5)'
    )
    
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=4, 
        help='Files per batch (default: 4, safe for timeout)'
    )
    
    args = parser.parse_args()
    
    if args.batches < 1 or args.batches > 20:
        print("❌ Number of batches must be between 1 and 20")
        sys.exit(1)
    
    if args.batch_size < 1 or args.batch_size > 10:
        print("❌ Batch size must be between 1 and 10")
        sys.exit(1)
    
    run_batch(batch_size=args.batch_size, max_batches=args.batches)


if __name__ == "__main__":
    main()