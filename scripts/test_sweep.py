#!/usr/bin/env python3
"""Test the monitoring sweep locally."""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from run_monitoring_sweep import run_monitoring_sweep


def main():
    """Run a test monitoring sweep and display results."""
    print("=" * 80)
    print("AGENTS CLI MONITORING - TEST SWEEP")
    print("=" * 80)
    print()

    # Use a test tracking file
    test_file = "data/agents_cli_mentions_test.md"
    print(f"Running sweep with tracking file: {test_file}")
    print()

    try:
        result = run_monitoring_sweep(test_file)

        print("RESULTS:")
        print("-" * 80)
        print(json.dumps(result, indent=2))
        print()

        if result.get("success"):
            print("\nSUMMARY:")
            print(f"  ✓ URLs found: {result.get('urls_found', 0)}")
            print(f"  ✓ URLs validated: {result.get('urls_validated', 0)}")
            print(f"  ✓ New URLs added: {result.get('new_urls_added', 0)}")
            print(f"  ✓ Duplicates skipped: {result.get('duplicates_skipped', 0)}")

            if result.get('sample_new_urls'):
                print("\n  Sample new URLs:")
                for url_data in result['sample_new_urls'][:5]:
                    print(f"    - {url_data.get('title', 'N/A')}")
                    print(f"      {url_data.get('url', 'N/A')}")
        else:
            print(f"\n❌ ERROR: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print()
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
