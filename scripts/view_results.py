#!/usr/bin/env python3
"""View tracking results from GCS or local file."""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tools.tracking import read_tracking_file


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="View Agents CLI monitoring results"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        default="data/agents_cli_mentions.md",
        help="Path to tracking file (local or GCS: gs://bucket/path)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of URLs to display",
    )
    return parser.parse_args()


def main():
    """Read and display tracking file contents."""
    args = parse_args()

    try:
        # Read tracking file
        result = read_tracking_file(args.file_path)
        data = json.loads(result)

        if not data.get("success"):
            print(f"Error reading file: {data.get('error', 'Unknown error')}", file=sys.stderr)
            return 1

        urls = data.get("urls", [])

        if args.json:
            # Output as JSON
            output = {
                "file_path": args.file_path,
                "total_urls": len(urls),
                "urls": urls[:args.limit] if args.limit else urls,
            }
            print(json.dumps(output, indent=2))
        else:
            # Output as formatted text
            print("=" * 80)
            print("AGENTS CLI MONITORING - TRACKING RESULTS")
            print("=" * 80)
            print(f"File: {args.file_path}")
            print(f"Total URLs tracked: {len(urls)}")
            print("=" * 80)
            print()

            # Group by domain
            by_domain = {}
            for url_data in urls:
                url = url_data.get("url", "")
                title = url_data.get("title", "Untitled")

                # Extract domain
                domain = ""
                if "://" in url:
                    domain = url.split("://")[1].split("/")[0]
                else:
                    domain = url.split("/")[0]

                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append((title, url))

            # Display grouped by domain
            for domain in sorted(by_domain.keys()):
                urls_list = by_domain[domain]
                print(f"{domain} ({len(urls_list)} URLs)")
                print("-" * 80)

                display_count = min(len(urls_list), args.limit) if args.limit else len(urls_list)
                for title, url in urls_list[:display_count]:
                    print(f"  • {title}")
                    print(f"    {url}")
                    print()

                if args.limit and len(urls_list) > args.limit:
                    print(f"  ... and {len(urls_list) - args.limit} more")
                    print()

            print("=" * 80)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
